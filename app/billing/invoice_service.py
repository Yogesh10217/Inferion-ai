import time
from datetime import datetime

from sqlalchemy import and_, select

from app.billing.cost_calculator import CostCalculator
from app.billing.models import Invoice, InvoiceLineItem, InvoiceStatus, OrganizationSubscription
from app.billing.pricing_service import PricingService
from app.limits.models import UsageRecord
from app.services.metrics_service import MetricsService


class InvoiceService:
    def __init__(self, session_factory, pricing_service: PricingService, metrics: MetricsService):
        self.session_factory = session_factory
        self.pricing = pricing_service
        self.metrics = metrics

    async def generate_invoice(self, org_id: str, start_time: datetime, end_time: datetime) -> Invoice:
        """
        Aggregates UsageRecords for an organization over a period and generates an Invoice.
        Remains completely decoupled from the real-time execution engine.
        """
        start_ms = time.time() * 1000

        async with self.session_factory() as db:
            # Find all usage records in this period
            stmt = select(UsageRecord).where(
                and_(
                    UsageRecord.organization_id == org_id,
                    UsageRecord.created_at >= start_time,
                    UsageRecord.created_at <= end_time,
                )
            )
            result = await db.execute(stmt)
            usages = list(result.scalars().all())

            # Group by provider and model
            grouped_usage = {}
            for usage in usages:
                key = (usage.provider, usage.model)
                if key not in grouped_usage:
                    grouped_usage[key] = {"requests": 0, "tokens": 0, "cost": 0.0, "currency": "USD"}

                grouped_usage[key]["requests"] += 1
                grouped_usage[key]["tokens"] += usage.total_tokens

                # Calculate cost for this single record
                rule = await self.pricing.get_rule_for_model(usage.provider, usage.model)
                if rule:
                    breakdown = CostCalculator.calculate_cost(usage, rule)
                    grouped_usage[key]["cost"] += breakdown.total
                    grouped_usage[key]["currency"] = breakdown.currency

            # Create the Invoice
            invoice = Invoice(
                organization_id=org_id,
                billing_period_start=start_time,
                billing_period_end=end_time,
                status=InvoiceStatus.GENERATED,
            )
            db.add(invoice)
            await db.flush()

            # Create Line Items
            subtotal = 0.0
            currency = "USD"
            for (provider, model), data in grouped_usage.items():
                line_item = InvoiceLineItem(
                    invoice_id=invoice.id,
                    provider=provider,
                    model=model,
                    requests=data["requests"],
                    tokens=data["tokens"],
                    cost=data["cost"],
                )
                db.add(line_item)
                subtotal += data["cost"]
                currency = data["currency"]

                # Record cost metric
                self.metrics.record_cost_incurred(provider, data["cost"])

            # Check for Subscription discounts
            sub_stmt = select(OrganizationSubscription).where(
                OrganizationSubscription.organization_id == org_id, OrganizationSubscription.status == "active"
            )
            sub_res = await db.execute(sub_stmt)
            active_sub = sub_res.scalars().first()

            discount = 0.0
            if active_sub and active_sub.plan:
                subtotal += active_sub.plan.monthly_price

            tax = subtotal * 0.0  # Optional tax calculation
            total = subtotal - discount + tax

            invoice.subtotal = round(subtotal, 6)
            invoice.tax = round(tax, 6)
            invoice.discount = round(discount, 6)
            invoice.total = round(total, 6)
            invoice.currency = currency

            await db.commit()
            await db.refresh(invoice)

        end_ms = time.time() * 1000
        self.metrics.record_invoice_generation(end_ms - start_ms)

        return invoice

    async def get_invoice(self, invoice_id: str) -> Invoice:
        stmt = select(Invoice).where(Invoice.id == invoice_id)
        async with self.session_factory() as db:
            res = await db.execute(stmt)
            return res.scalars().first()

    async def list_invoices(self, org_id: str) -> list[Invoice]:
        stmt = select(Invoice).where(Invoice.organization_id == org_id).order_by(Invoice.generated_at.desc())
        async with self.session_factory() as db:
            res = await db.execute(stmt)
            return list(res.scalars().all())

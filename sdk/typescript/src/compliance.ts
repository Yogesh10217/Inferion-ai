/**
 * TypeScript SDK Client for Enterprise AI Compliance Platform (Phase 5.27).
 */

export class ComplianceClient {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async adoptFramework(frameworkType: string, name: string, description: string = 'Framework'): Promise<any> {
    return this.client.request('POST', '/v1/compliance/frameworks', {
      framework_type: frameworkType,
      name,
      description,
    });
  }

  async listFrameworks(): Promise<any[]> {
    return this.client.request('GET', '/v1/compliance/frameworks');
  }

  async registerControl(code: string, name: string, description: string, controlType: string = 'PREVENTIVE', category: string = 'SECURITY'): Promise<any> {
    return this.client.request('POST', '/v1/compliance/controls', {
      code,
      name,
      description,
      control_type: controlType,
      category,
    });
  }

  async listControls(): Promise<any[]> {
    return this.client.request('GET', '/v1/compliance/controls');
  }

  async collectEvidence(idempotencyKey: string, subjectType: string, subjectId: string, requiredTypes: string[]): Promise<any> {
    return this.client.request('POST', '/v1/compliance/evidence/collect', {
      idempotency_key: idempotencyKey,
      subject_type: subjectType,
      subject_id: subjectId,
      required_evidence_types: requiredTypes,
    });
  }

  async runAssessment(frameworkId: string, subjectId: string = 'global'): Promise<any> {
    return this.client.request('POST', '/v1/compliance/assessments', {
      framework_id: frameworkId,
      subject_id: subjectId,
    });
  }

  async getPosture(): Promise<any> {
    return this.client.request('GET', '/v1/compliance/posture');
  }

  async generateAssuranceReport(frameworkId: string, conclusion: string = 'ASSURED'): Promise<any> {
    return this.client.request('POST', '/v1/compliance/assurance', {
      framework_id: frameworkId,
      conclusion,
    });
  }

  async createAuditPackage(frameworkId: string, evidenceBundleRef: string, assuranceReportRef: string): Promise<any> {
    return this.client.request('POST', '/v1/compliance/audit-packages', {
      framework_id: frameworkId,
      evidence_bundle_reference: evidenceBundleRef,
      assurance_report_reference: assuranceReportRef,
    });
  }

  async getAnalytics(): Promise<any> {
    return this.client.request('GET', '/v1/compliance/analytics');
  }
}

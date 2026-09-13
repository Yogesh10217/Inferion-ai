# Blue-Green Deployment Runbook

## 1. Procedure
1. **Blue (Active)**: Currently serving live production traffic.
2. **Green (Idle)**: Deploy release candidate to Green cluster.
3. **Pre-cutover Validation**: Run health probes, database checks, and smoke tests against Green.
4. **Traffic Cutover**: Switch router/load balancer from Blue to Green.
5. **Post-cutover Monitoring**: Monitor Green metrics for 15 minutes.
6. **Decommission**: Tear down or convert Blue into standby.

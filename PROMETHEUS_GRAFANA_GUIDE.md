# Prometheus and Grafana Integration Guide

This guide explains how Prometheus and Grafana integrate with CertOps and how to use them effectively.

## Table of Contents

- [Overview](#overview)
- [Prometheus Integration](#prometheus-integration)
  - [What Prometheus Provides](#what-prometheus-provides)
  - [Metrics Collected](#metrics-collected)
  - [PromQL Queries](#promql-queries)
  - [Configuration](#configuration)
- [Grafana Integration](#grafana-integration)
  - [What Grafana Provides](#what-grafana-provides)
  - [Dashboards](#dashboards)
  - [Alerting](#alerting)
- [Setup and Configuration](#setup-and-configuration)
- [Using Prometheus and Grafana](#using-prometheus-and-grafana)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Overview

CertOps uses **Prometheus** for metrics collection and **Grafana** for visualization and monitoring. Together, they provide real-time insights into system health and enable data-driven remediation decisions.

### Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                            CERT-OPS ARCHITECTURE                            │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────────────────────┐  │
│  │             │    │             │    │                           │  │
│  │  Kubernetes  │───▶│  Prometheus │───▶│        CertOps            │  │
│  │  Cluster     │    │  (Metrics)  │    │        Pipeline           │  │
│  │             │    │             │    │                           │  │
│  └─────────────┘    └─────────────┘    └───────────────────────────┘  │
│                                                                               │
│  ┌─────────────┐                                                                 │
│  │             │                                                                 │
│  │   Grafana   │◀─────────────────────────────────────────────────────────────┘  │
│  │  (Dashboard)│                                                                 │
│  │             │                                                                 │
│  └─────────────┘                                                                 │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Prometheus Integration

### What Prometheus Provides

Prometheus is a **time-series database** and **monitoring system** that:

1. **Collects metrics** from Kubernetes pods and services
2. **Stores time-series data** with high precision
3. **Provides PromQL query language** for analysis
4. **Supports alerting** based on metric thresholds
5. **Scrapes metrics** from HTTP endpoints

### Metrics Collected by CertOps

CertOps queries the following metrics from Prometheus:

| Metric | PromQL Query | Purpose |
|--------|-------------|---------|
| **CPU Usage** | `container_cpu_usage_seconds_total` | Detect CPU saturation |
| **Memory Usage** | `container_memory_usage_bytes` | Detect memory pressure |
| **Latency (p95)** | `http_request_duration_seconds_bucket` | Measure response times |
| **Traffic** | `http_requests_total` | Monitor request rate |
| **Error Rate** | `http_requests_total{status=~"5.."}` | Track error rates |

### PromQL Queries Used by CertOps

#### CPU Usage Percentage

```promql
avg(
    rate(container_cpu_usage_seconds_total{
        namespace="{namespace}",
        container!=""
    }[5m])
) * 100
```

**Purpose**: Calculate average CPU usage percentage for pods in a namespace

#### Memory Usage Percentage

```promql
avg(
    container_memory_usage_bytes{
        namespace="{namespace}",
        container!=""
    } /
    container_spec_memory_limit_bytes{
        namespace="{namespace}",
        container!=""
    } * 100
)
```

**Purpose**: Calculate average memory usage percentage for pods in a namespace

#### Latency (p95)

```promql
histogram_quantile(0.95,
    sum(rate(http_request_duration_seconds_bucket{
        namespace="{namespace}"
    }[5m])) by (le)
) * 1000
```

**Purpose**: Calculate 95th percentile latency in milliseconds

#### Traffic (Requests per Second)

```promql
sum(rate(http_requests_total{
    namespace="{namespace}"
}[5m]))
```

**Purpose**: Calculate requests per second

#### Error Rate

```promql
sum(rate(http_requests_total{
    namespace="{namespace}",
    status=~"5.."
}[5m])) /
sum(rate(http_requests_total{
    namespace="{namespace}"
}[5m])) * 100
```

**Purpose**: Calculate percentage of 5xx errors

### Configuration

Prometheus configuration is in `config/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
```

## Grafana Integration

### What Grafana Provides

Grafana is a **visualization platform** that:

1. **Creates dashboards** for monitoring
2. **Supports multiple data sources** (Prometheus, Loki, etc.)
3. **Provides alerting UI** for managing alerts
4. **Allows customizable visualizations** (graphs, tables, gauges)
5. **Supports templating** for dynamic dashboards

### Dashboards

CertOps includes pre-configured Grafana dashboards:

#### 1. CertOps Overview Dashboard

**Purpose**: High-level view of system health

**Panels**:
- CPU Usage (namespace breakdown)
- Memory Usage (namespace breakdown)
- Latency Distribution
- Error Rate
- Traffic Volume
- Incident Count

#### 2. CertOps Detailed Metrics Dashboard

**Purpose**: Detailed metrics for troubleshooting

**Panels**:
- Per-pod CPU usage
- Per-pod Memory usage
- Latency percentiles (p50, p90, p95, p99)
- Request rate by endpoint
- Error rate by status code
- Pod restarts

#### 3. CertOps Remediation Dashboard

**Purpose**: Track remediation actions

**Panels**:
- Remediation actions executed
- Success rate by action type
- Latency improvement by remediation
- Cost impact of remediations
- Time to remediation

### Alerting

Grafana alerts can be configured to notify when:

1. **CPU usage exceeds 80%** for 5 minutes
2. **Memory usage exceeds 90%** for 5 minutes
3. **Latency exceeds 500ms** for 10 minutes
4. **Error rate exceeds 5%** for 5 minutes
5. **Pod restarts exceed threshold**

## Setup and Configuration

### Starting Prometheus and Grafana

```bash
# From CertOps directory
cd /f/Projects/CertOps

# Start containers
docker-compose up -d

# Verify containers are running
docker ps
```

### Accessing Prometheus

- **URL**: http://localhost:9090
- **Username**: (none)
- **Password**: (none)

### Accessing Grafana

- **URL**: http://localhost:3000
- **Username**: admin
- **Password**: admin

### Configuring Grafana Data Source

1. Log in to Grafana (admin/admin)
2. Click "Configuration" (gear icon) → "Data Sources"
3. Click "Add data source"
4. Select "Prometheus"
5. Set URL to: `http://prometheus:9090`
6. Click "Save & Test"

### Importing Dashboards

Grafana dashboards are configured in `config/grafana/provisioning/dashboards/`.

To import a dashboard manually:

1. Click "+" → "Import"
2. Enter dashboard ID or upload JSON file
3. Select Prometheus as data source
4. Click "Import"

## Using Prometheus and Grafana

### Querying Metrics in Prometheus

1. Open Prometheus at http://localhost:9090
2. Click "Graph" tab
3. Enter PromQL query in the query box
4. Click "Execute"
5. View results in graph form

Example queries:

```promql
# CPU usage for all pods
container_cpu_usage_seconds_total

# Memory usage for specific namespace
container_memory_usage_bytes{namespace="default"}

# Latency distribution
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

### Creating Dashboards in Grafana

1. Open Grafana at http://localhost:3000
2. Click "+" → "Dashboard" → "New dashboard"
3. Click "Add visualization"
4. Select Prometheus data source
5. Enter PromQL query
6. Customize visualization (graph type, axes, thresholds)
7. Click "Apply"
8. Add more panels as needed
9. Click "Save dashboard"

### Monitoring CertOps Incidents

1. Open CertOps Overview dashboard
2. Monitor CPU, memory, latency, and error rate
3. Watch for anomalies that indicate incidents
4. Use Detailed Metrics dashboard to drill down
5. Check Remediation dashboard to track fixes

## Troubleshooting

### Prometheus Not Collecting Metrics

**Symptoms**: No metrics appearing in Prometheus

**Solutions**:

```bash
# Check Prometheus logs
docker logs prometheus

# Verify targets are being scraped
# Go to http://localhost:9090/targets

# Check if pods have annotations
docker exec -it prometheus cat /etc/prometheus/prometheus.yml
```

### Grafana Not Showing Data

**Symptoms**: Grafana dashboards show "No data"

**Solutions**:

1. Verify data source is configured correctly
2. Check data source connection
3. Verify PromQL queries are correct
4. Check time range in dashboard

### High Cardinality Metrics

**Symptoms**: Prometheus using too much memory

**Solutions**:

1. Review scrape configuration
2. Add relabeling to reduce cardinality
3. Increase Prometheus resources

### Alerts Not Firing

**Symptoms**: Expected alerts not appearing

**Solutions**:

1. Check alert rules in Grafana
2. Verify alert conditions
3. Check notification channels
4. Test alert manually

## Advanced Usage

### Custom Metrics

To add custom metrics:

1. Create a metrics endpoint in your application
2. Add Prometheus annotations to pods:
   ```yaml
   annotations:
     prometheus.io/scrape: "true"
     prometheus.io/port: "8000"
     prometheus.io/path: "/metrics"
   ```
3. Update Prometheus configuration
4. Restart Prometheus

### Custom Dashboards

To create custom dashboards:

1. Use Grafana's dashboard editor
2. Add panels for your custom metrics
3. Save dashboard
4. Export JSON for version control

### Alerting Rules

To create alerting rules:

1. Go to Alerting → Notification policies
2. Add notification channel (Email, Slack, etc.)
3. Go to Alerting → Alert rules
4. Click "New alert rule"
5. Configure query and conditions
6. Set notification channel
7. Save rule

### Recording Rules

To create recording rules for complex queries:

1. Edit Prometheus configuration
2. Add recording rules:
   ```yaml
   rule_files:
     - 'recording_rules.yml'
   ```
3. Create `recording_rules.yml`:
   ```yaml
   groups:
     - name: example
       rules:
         - record: job:http_requests_total:rate5m
           expr: rate(http_requests_total[5m])
   ```
4. Restart Prometheus

## Best Practices

### Prometheus Best Practices

1. **Use meaningful metric names**: Follow naming conventions
2. **Label wisely**: Use labels for filtering, not for storing data
3. **Set appropriate scrape intervals**: Balance between freshness and load
4. **Monitor Prometheus itself**: Set up alerts for Prometheus health
5. **Retention policy**: Configure appropriate retention based on needs

### Grafana Best Practices

1. **Use templates**: Create reusable dashboard templates
2. **Organize dashboards**: Use folders to organize dashboards
3. **Set up alerts**: Configure alerts for critical metrics
4. **Use annotations**: Add annotations for important events
5. **Document dashboards**: Add descriptions and documentation

## Summary

### Prometheus Contributions

✅ **Real-time metrics collection** from Kubernetes pods
✅ **Time-series database** for storing historical metrics
✅ **PromQL query language** for analyzing metrics
✅ **Alerting** based on metric thresholds
✅ **Integration with CertOps** for data-driven remediation

### Grafana Contributions

✅ **Visualization dashboard** for metrics
✅ **Customizable dashboards** for different use cases
✅ **Alerting UI** for managing alerts
✅ **Data source integration** with Prometheus
✅ **Real-time monitoring** of CertOps operations

### Key Benefits

1. **Visibility**: Real-time insights into system health
2. **Proactive Monitoring**: Detect issues before they become incidents
3. **Data-Driven Decisions**: Use metrics to guide remediation
4. **Historical Analysis**: Track trends over time
5. **Alerting**: Get notified of critical issues
6. **Integration**: Seamless integration with CertOps pipeline

By leveraging Prometheus and Grafana, CertOps can make **informed, data-driven remediation decisions** with full visibility into system health and performance.

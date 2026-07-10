---
access_level: confidential
allowed_roles:
- apollo-devs
- Administrator
allowed_users: []
canonical_document_id: doc-016-apollo
created_at: 2026-04-10
department: engineering
description: Current architecture document for Project Apollo backend services.
document_id: doc-016-apollo
expected_evaluation_categories: engineering, apollo, architecture
is_current_version: true
source_trust_level: official
source_type: markdown
title: Project Apollo Technical Specifications
updated_at: 2026-04-20
version: 2
---

# Project Apollo Technical Specifications v2

This document describes the final microservices architecture for Project Apollo.

## Database Technologies
We are using **Spanner** as our global transactional database, with **Redis** as a distributed caching layer to maintain latencies under 50ms.

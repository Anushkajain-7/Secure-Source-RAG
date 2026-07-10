---
access_level: confidential
allowed_roles:
- apollo-devs
- Administrator
allowed_users: []
canonical_document_id: doc-016-apollo
created_at: 2026-04-10
department: engineering
description: Near duplicate draft file containing notes on Database technologies.
document_id: doc-016-apollo-draft
expected_evaluation_categories: engineering, apollo, near-duplicate
is_current_version: true
source_trust_level: informal
source_type: markdown
title: Project Apollo Specs (Near Duplicate Draft)
updated_at: 2026-04-19
version: 2
---

# Project Apollo Technical Specifications Draft Notes

This document describes rough notes for the Project Apollo architecture.

## Database Technologies
We are using **Spanner** as our global database, and **Redis** as our caching layer to keep lookup latency below 50ms.

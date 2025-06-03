---
title: Architecture
prev: docs/how-it-works
next: docs/installation/
weight: 2
---

<!--
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
-->

The Parliamentary Question Responder is built on a modular, cloud-based architecture designed for security, scalability, and with an ingestion mechanism from government systems.

![Similar](/docs/images/architecture.png "PQ Parliamentary Question Responder Architecture") 

## Key Components

This architecture ensures that the Parliamentary Question Responder can be deployed securely within government environments while providing the flexibility to adapt to specific departmental needs and workflows.

**Data Ingestion Layer**

* Connects to government data sources (in this case https://questions-statements-api.parliament.uk) 
* Processes and indexes the parliament questions into knowledge bases.
* The data can be periodically refreshed to ensure access to the latest published answers.

**AI Processing Engine**

* Leverages Amazon Bedrock's generative AI capabilities to performance semantic search for identifying similar questions, or draft responses against guidelines and parliament documentation.
* Maintains context awareness across indexed data sources.

**Response Generation System**

* Creates draft responses following parliamentary writing conventions.
* Maintains citation links to source documents.

**API Integration Framework**

* RESTful APIs for seamless integration with existing workflow systems
* Secure authentication and authorization controls

**User Interface Layer**

* Intuitive web-based interface for analysts
* Secure access managed through Amazon Cognito




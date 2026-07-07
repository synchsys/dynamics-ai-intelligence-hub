# Generic CRM — Entity-Relationship Diagram

Client-agnostic CRM domain (#8), modelled on **native Dataverse standard tables**
with custom `racy_` tables only for AI logging (ADR-0005). `UK` marks a
**Dataverse alternate key** (used for upsert); `PK` the GUID primary key; `FK` a
lookup. Cross-cutting entities (Activity, Document, Audit Event, AI Request) use
a **polymorphic** lookup that can point at several tables — see
[crm-schema-notes.md](../architecture/crm-schema-notes.md); only representative
edges are drawn here to keep the diagram legible.

```mermaid
erDiagram
    ACCOUNT ||--o{ CONTACT : employs
    ACCOUNT ||--o{ OPPORTUNITY : "has"
    ACCOUNT ||--o{ INCIDENT : "raises"
    CONTACT ||--o{ OPPORTUNITY : "primary contact"
    CONTACT ||--o{ INCIDENT : "primary contact"
    LEAD ||--o| OPPORTUNITY : "qualifies to"
    OPPORTUNITY }o--o{ PRODUCT : "line items"
    INCIDENT }o--o{ KNOWLEDGEARTICLE : "resolved by"

    ACCOUNT ||--o{ ACTIVITY : "regarding"
    CONTACT ||--o{ ACTIVITY : "regarding"
    OPPORTUNITY ||--o{ ACTIVITY : "regarding"
    INCIDENT ||--o{ ACTIVITY : "regarding"

    ACCOUNT ||--o{ DOCUMENT : "attached to"
    INCIDENT ||--o{ DOCUMENT : "attached to"
    KNOWLEDGEARTICLE ||--o{ DOCUMENT : "attached to"

    SYSTEMUSER ||--o{ AUDIT_EVENT : "actor"
    ACCOUNT ||--o{ AUDIT_EVENT : "audited"
    CONTACT ||--o{ AUDIT_EVENT : "audited"
    INCIDENT ||--o{ AUDIT_EVENT : "audited"

    SYSTEMUSER ||--o{ AI_REQUEST : "requested by"
    ACCOUNT ||--o{ AI_REQUEST : "acts on"
    CONTACT ||--o{ AI_REQUEST : "acts on"
    INCIDENT ||--o{ AI_REQUEST : "acts on"
    AI_REQUEST ||--|| AI_RESPONSE : "answered by"

    ACCOUNT {
        uniqueidentifier accountid PK
        string name "primary name"
        string accountnumber UK "alt key"
        uniqueidentifier primarycontactid FK
    }
    CONTACT {
        uniqueidentifier contactid PK
        string fullname "primary name"
        string emailaddress1 UK "alt key"
        uniqueidentifier parentcustomerid FK "account"
    }
    LEAD {
        uniqueidentifier leadid PK
        string subject "primary name"
        string racy_leadcode UK "alt key (added)"
        uniqueidentifier parentcontactid FK
    }
    OPPORTUNITY {
        uniqueidentifier opportunityid PK
        string name "primary name"
        string racy_opportunitycode UK "alt key (added)"
        uniqueidentifier parentaccountid FK
        uniqueidentifier parentcontactid FK
        uniqueidentifier originatingleadid FK
    }
    INCIDENT {
        uniqueidentifier incidentid PK
        string title "primary name"
        string ticketnumber UK "alt key (system)"
        uniqueidentifier customerid FK "account or contact"
        uniqueidentifier primarycontactid FK
    }
    PRODUCT {
        uniqueidentifier productid PK
        string name "primary name"
        string productnumber UK "alt key"
    }
    KNOWLEDGEARTICLE {
        uniqueidentifier knowledgearticleid PK
        string title "primary name"
        string articlepublicnumber UK "alt key"
    }
    ACTIVITY {
        uniqueidentifier activityid PK
        string subject "primary name"
        string activitytypecode "task/email/phonecall"
        uniqueidentifier regardingobjectid FK "polymorphic"
    }
    DOCUMENT {
        uniqueidentifier annotationid PK
        string subject "primary name"
        string filename
        uniqueidentifier objectid FK "polymorphic (regarding)"
    }
    AUDIT_EVENT {
        uniqueidentifier auditid PK
        datetime createdon
        int action "create/update/delete"
        uniqueidentifier objectid FK "audited record (polymorphic)"
        uniqueidentifier userid FK "systemuser"
    }
    AI_REQUEST {
        uniqueidentifier racy_airequestid PK
        string racy_requestcode UK "alt key"
        string racy_purpose "crm-assistant/rag/wager-intake"
        string racy_model
        string racy_prompt "memo"
        string racy_userid FK "acting user"
        uniqueidentifier racy_regardingid FK "CRM record acted on (design)"
    }
    AI_RESPONSE {
        uniqueidentifier racy_airesponseid PK
        string racy_requestcode UK "alt key -> pairs to request"
        string racy_rawoutput "memo"
        string racy_decision
        boolean racy_ok
        int racy_tokens
        int racy_latencyms
    }
    SYSTEMUSER {
        uniqueidentifier systemuserid PK
        string fullname
        string domainname UK
    }
```

## How to read it

- **`||--o{`** one-to-many · **`||--o|`** one-to-zero-or-one · **`}o--o{`**
  many-to-many · **`||--||`** one-to-one.
- **`UK`** = Dataverse **alternate key** — the natural business identifier used
  for idempotent upsert (seeding/integration), since standard tables key on a
  GUID `PK`. `(added)` marks alt keys that must be *created* on a standard table
  (they don't ship with a business-natural one).
- **Polymorphic** lookups (`regardingobjectid`, `objectid`,
  `racy_regardingid`) can target several tables; the drawn edges are
  representative, not exhaustive.

Detail — cascade behaviour, the polymorphic targets, and the AI ↔ CRM link — is
in [crm-schema-notes.md](../architecture/crm-schema-notes.md).

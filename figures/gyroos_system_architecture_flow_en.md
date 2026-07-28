# GyroOS System Architecture and Flow

```mermaid
flowchart TB

    GL["Gyro Logic Core\nStructure → Slice → Stability"]

    subgraph OS["GyroOS Runtime Layer"]
        API["Runtime API\n/loop/step"]
        PE["ProcessExecutor"]
        RR["Runtime Records / History\nCurrent Scope · Process · Memory · Trajectory"]
        OR["OperatorResponse\nContinue · Stop · Jump · Reslice · Defer · Adjust"]

        API --> PE
        PE --> RR
        PE --> OR
        OR --> PE
    end

    subgraph VN["vNext Read-Only Projection Layer"]
        RP["Read-Only Runtime Projection"]
        SC["Stability Scene / Observation"]
        BE["Boundary Evaluation"]
        SA["Semantic Assembly / Readability / Trajectory Views"]

        RP --> SC
        SC --> BE
        BE --> SA
    end

    subgraph INS["Inspection API Layer\n/vnext/experimental"]
        IR["Dedicated Inspection Router\nPOST-only · request-local · read-only"]
        EH["Shared Error Response Helper"]
        VU["Small Pure Validation Utility\nCanonical JSON UTF-8 Size"]

        IR --> EH
        IR --> VU
    end

    subgraph HIER["Inspection Contract Hierarchy F–W"]
        F["F Receipt"]
        G["G Batch Manifest"]
        H["H Manifest Comparison"]
        I["I Comparison Review Bundle"]
        J["J Review-Bundle Comparison"]
        K["K Review-Bundle Comparison Set"]
        L["L Set Comparison"]
        M["M Comparison Series"]
        N["N Series Comparison"]
        O["O Comparison Collection"]
        P["P Collection Comparison"]
        Q["Q Comparison Sequence"]
        R["R Sequence Comparison"]
        S["S Comparison Register"]
        T["T Register Comparison"]
        U["U Comparison Ledger"]
        V["V Ledger Comparison"]
        W["W Comparison Archive"]

        F --> G --> H --> I --> J --> K --> L --> M --> N --> O --> P --> Q --> R --> S --> T --> U --> V --> W
    end

    subgraph AUTH["GyroAuth Consumer Boundary"]
        CB["Consumer Compatibility Boundary"]
        AUTHC["GyroAuth / External Consumers"]

        CB --> AUTHC
    end

    GL --> OS
    RR -. "explicit read-only source" .-> RP
    SA -. "non-canonical projection" .-> IR
    IR --> F
    W -. "explicit references only" .-> CB

    GL -. "defines principles" .-> VN
    OS -. "does not depend on" .-> AUTH
    INS -. "no Runtime mutation\nno canonical persistence\nno semantic/risk/auth aggregation" .-> AUTH

    classDef core fill:#ffffff,stroke:#222,stroke-width:2px;
    classDef runtime fill:#f7f7f7,stroke:#444,stroke-width:1.5px;
    classDef projection fill:#fbfbfb,stroke:#666,stroke-dasharray: 4 3;
    classDef inspection fill:#ffffff,stroke:#555,stroke-width:1.5px;
    classDef contract fill:#fcfcfc,stroke:#777;
    classDef consumer fill:#ffffff,stroke:#333,stroke-width:1.5px;

    class GL core;
    class API,PE,RR,OR runtime;
    class RP,SC,BE,SA projection;
    class IR,EH,VU inspection;
    class F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W contract;
    class CB,AUTHC consumer;
```

## Reading the Diagram

- `Gyro Logic Core` defines the invariant order `Structure → Slice → Stability`.
- `GyroOS Runtime` executes bounded processes and owns Runtime state, history, and persistence boundaries.
- `vNext Read-Only Projection` observes Runtime outputs without changing Runtime state.
- `Inspection API` exposes request-local, POST-only inspection contracts.
- Gates `F–W` form an explicit-reference hierarchy. The arrows do not imply chronology, semantic trend, risk, authentication state, or Runtime continuation.
- `GyroAuth` and other consumers remain outside GyroOS. They consume explicit outputs through the consumer compatibility boundary.

## Boundary Rules

```text
request-local
read-only
non-canonical
explicit references only
no implicit retrieval
no Runtime mutation
no canonical persistence
no semantic inference
no risk aggregation
no authentication aggregation
```

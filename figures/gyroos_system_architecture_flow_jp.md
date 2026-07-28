# GyroOS システム構成図・フロー図

```mermaid
flowchart TB

    GL["Gyro Logic Core\nStructure → Slice → Stability"]

    subgraph OS["GyroOS Runtime Layer"]
        API["Runtime API\n/loop/step"]
        PE["ProcessExecutor"]
        RR["Runtime Records / History\nCurrent Scope・Process・Memory・Trajectory"]
        OR["OperatorResponse\nContinue・Stop・Jump・Reslice・Defer・Adjust"]

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
        IR["Dedicated Inspection Router\nPOSTのみ・request-local・read-only"]
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
    RR -. "明示的なread-only source" .-> RP
    SA -. "non-canonical projection" .-> IR
    IR --> F
    W -. "explicit references only" .-> CB

    GL -. "原理を定義" .-> VN
    OS -. "依存しない" .-> AUTH
    INS -. "Runtime mutationなし\ncanonical persistenceなし\nsemantic・risk・auth aggregationなし" .-> AUTH

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

## 図の読み方

- `Gyro Logic Core`は、不変順序である`Structure → Slice → Stability`を定義します。
- `GyroOS Runtime`は、bounded processを実行し、Runtime state、history、persistence boundaryを所有します。
- `vNext Read-Only Projection`は、Runtime stateを変更せずにRuntime outputを観測します。
- `Inspection API`は、request-localかつPOSTのみのinspection contractを公開します。
- Gate `F–W`は、明示的参照による階層です。矢印は、時間順、意味的傾向、risk、authentication state、Runtime continuationを意味しません。
- `GyroAuth`および外部consumerはGyroOSの外側にあり、consumer compatibility boundaryを通して明示的outputを利用します。

## 境界ルール

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

# GyroOS：Structure–Slice–Stability、Read-Only Projection、明示的Inspection ContractのためのBounded Runtime Architecture

> **翻訳版作業コピー／未投稿**  
> 本文書は、英語原版をJxivへ先行投稿し、スクリーニング後に公開された版を翻訳元として整合させるための作業コピーである。英語原版の公開前には、日本語版をJxivへ投稿しない。
>
> 英語原版公開後、以下を確定情報へ置換する。
>
> ```text
> English original title: [PENDING]
> Authors: [PENDING]
> Jxiv DOI: [PENDING]
> Public release year: [PENDING]
> ```
>
> 最終投稿版の冒頭には、次の趣旨を明記する。
>
> 本稿は、Jxivで公開された英語原版「[English title]」（[authors], [year], DOI: [jxiv DOI]）の日本語翻訳版である。翻訳版の内容は英語原版に忠実であり、原版にないデータ、解釈、主張を追加していない。
>
> 翻訳補助または言語調整に生成AIを使用した場合は、実際の使用方法に即して次の趣旨を明記する。
>
> 本翻訳版の作成には生成AIを翻訳補助および言語調整に使用した。著者が英語原版との対応を全編確認し、翻訳の正確性および最終内容について全責任を負う。

## 要旨

Gyro Logicは、不変の成立順序を`Structure → Slice → Stability`として定義する。この順序を有限な計算資源上へ実装する際には、Runtime continuityを一つの現在stateへ還元せず、canonical historyを書き換えず、下流の解釈が観測対象となるRuntime自体を変更しないarchitectureが必要になる。本稿は、GyroOS v4.0.0を、bounded execution、canonical Runtime ownership、read-only projection、non-canonical Inspection、外部consumer interpretationの5つを分離するbounded Runtime architectureとして提示する。1つのbounded requestは`/loop/step`を通じて1つのbounded Gyro Processを実行し、canonicalなProcess、Trajectory、current-scope、Memory recordはRuntimeが所有する。vNext projectionは明示的に与えられたRuntime outputをRuntime stateを変更せずに観測する。POST-onlyのInspection contract F–Wは、明示的参照を用いてrequest-localなartifactを構成する。GyroAuthはGyroOS実装境界の外側にあるconsumerとして位置付けられる。現実装はsingle-hostかつSQLite-backedであり、vNext Inspection contractはexperimentalである。本稿の貢献はGyro Logicの完全な数理形式化ではなく、execution、persistence、projection、inspection、consumptionを分離することで、有限資源上でも不変Coreを保持できる実装境界を示すことにある。

## 1. はじめに

Gyro Logicの不変Coreは次である。

```text
Structure → Slice → Stability
```

GyroOSは、このCoreをRuntime systemとして実装する実行層である。実装上の問題は、単に計算結果を得ることではない。有限な計算機は、1つのrequestで何を実行するか、実行後に何を保持するか、何をcanonical Runtime historyとみなすか、どのderived viewをread-onlyに保つか、どこから外部解釈が始まるかを決めなければならない。

一般的な実装では、これらの関心が容易に混在する。current stateがTrajectory全体であるかのように扱われることがある。derived projectionがcanonical historyへ書き戻されることがある。Inspection outputに、Runtimeが生成していないsemantic、risk、authenticationの意味が付与されることもある。このような結合は、実装都合によって理論Coreの意味を変えてしまう。

GyroOS v4.0.0は、これらを明示的なarchitecture boundaryとして分離する。bounded executionをpersistenceから分離し、canonical Runtime recordをderived viewから分離し、read-only projectionをInspectionから分離し、Inspection artifactを外部consumer decisionから分離する。したがって、次の方向を保持する。

```text
Gyro Logic
↓
GyroOS
↓
GyroAuth / external consumers
```

この方向は、GyroOSがGyroAuthへ依存することを意味しない。

本稿が扱うimplementation snapshotは、GitHub Release `v4.0.0`およびZenodo record `21641158`によって固定されている。

## 2. 理論境界

### 2.1 Structure、Slice、Stability

不変のGyro Unitは次である。

```text
Structure → Slice → Stability
```

`Structure`は、成立が可能であり続ける様式である。`Slice`は、Structureの中に成立へ向かう道筋を開く。`Stability`は、その開かれた道筋が継続可能な一つの成立として読める状態である。

GyroOSは、このCoreへ新しいstageを追加しない。RuntimeはSlice内部を次のように区別できる。

```text
Slice {
  Operator Orientation
  → slice-ing
  → slice-done
}
```

これらはSlice内部の実装上の区別であり、不変順序を再定義するものではない。

### 2.2 Gyro ProcessとOperator Response

bounded Gyro Processは、不変Coreを時間を含むRuntime上で読むものである。

```text
Structure
→ Slice {
    Operator Orientation
    → slice-ing
    → slice-done
  }
→ Stability
→ Operator Response
```

Operator Responseは不変Core sequenceの外側にある。Stabilityが利用可能になった後、Runtimeをどのように続けるかを決定する。現在のresponse categoryには、`Continue`、`Stop`、`Jump`、`Reslice`、`Defer`、`Adjust`がある。

したがって、Gyro Loopは`Structure → Slice → Stability`の代替ではない。Operator Responseを介してbounded Gyro Processが反復される構造である。

### 2.3 Trajectory

Trajectoryは、一つの可変なcurrent stateとして表現されない。Runtime continuityは、bounded Process result、current-scope reference、Memory record、Trajectory edgeの明示的に保持された関係から再構成される。このarchitectureは、完全なTrajectoryを余すところなく取得したと主張しない。continuityを最新resultだけへ還元しないために、有限なrecordとして何を保持すべきかを定義する。

## 3. Bounded Runtime Architecture

### 3.1 1 Request、1 Bounded Process

主要な実行endpointは次である。

```text
POST /loop/step
```

1つのrequestは1つのbounded Gyro Processを実行する。`ProcessExecutor`は明示的requestを読み、StructureとSliceのRuntime interpretationを適用し、Stabilityに関するoutputを生成し、Operator Responseを選択し、次のbounded execution relationを準備する。

bounded executionは理論Coreの変更ではなく、実装原理である。1回のRuntime operationへ有限の境界を設定しながら、次のProcessへ継続する可能性を保持する。

### 3.2 Runtime Query Surface

Runtimeは、current scope、Process history、Trajectory、Process record、Memory recordに対するbounded query surfaceも公開する。これらのqueryは、新しいProcessを実行しない。hidden latest stateを推定せず、Operator Responseを選択せず、record absenceをStability、VOID、DEFER、STOPとして再解釈しない。

この分離により、observationが暗黙にexecutionへ変化することを防ぐ。

## 4. Canonical Runtime Ownership

GyroOSは、次のRuntime-managed recordへcanonical ownershipを割り当てる。

```text
current scope
Process records
Trajectory history
Memory records
```

現実装では、atomicなSQLite-backed repository boundaryを使用する。完全なProcess result groupをatomicにpublishし、その後current-scope pointerを更新し、immutableなProcessおよびTrajectory historyを保持する。restart後のtyped reconstructionにより、記録済みRuntime contractを再構成する。

canonical ownershipが重要なのは、後続のprojectionやinspectionが有用なderived representationを生成し得るためである。それらのrepresentationが、元となるRuntime recordを暗黙に置き換えてはならない。

現実装はsingle-hostかつSQLite-backedである。distributed consensus、multi-node continuity、public Internet deployment readinessは主張しない。

## 5. Read-Only vNext Projection

vNext projection layerは、明示的に与えられたRuntime outputを観測する。そのboundaryは次である。

```text
explicit Runtime source
→ read-only observation
→ non-canonical projection
```

projectionは、Stability scene、observation、Boundary evaluation、readability assembly、Trajectory viewなどを構成できる。ただし、次を行ってはならない。

```text
Runtime stateを変更する
Operator Responseを選択する
canonical historyを書き換える
implicit latest sourceを推定する
authentication stateを生成する
risk stateを生成する
canonical persistenceになる
```

この分離により、すべてのderived viewを新しいRuntime factとして扱うことなく、より豊かなinspectionを可能にする。

## 6. Inspection APIと明示的F–W Contract

### 6.1 Inspection Boundary

Inspection APIは、承認されたexperimental boundaryで公開される。

```text
/vnext/experimental
```

Inspection endpointはPOST-only、request-local、read-only、non-canonicalである。明示的なrequest contentとexplicit referenceに対して動作する。repository-backedなInspection retrievalやmutationは導入しない。

### 6.2 Contract Hierarchy

実装済みhierarchyは次である。

```text
F Receipt
→ G Batch Manifest
→ H Manifest Comparison
→ I Comparison Review Bundle
→ J Review-Bundle Comparison
→ K Review-Bundle Comparison Set
→ L Set Comparison
→ M Comparison Series
→ N Series Comparison
→ O Comparison Collection
→ P Collection Comparison
→ Q Comparison Sequence
→ R Sequence Comparison
→ S Comparison Register
→ T Register Comparison
→ U Comparison Ledger
→ V Ledger Comparison
→ W Comparison Archive
```

各contractは、明示的に与えられたinputまたはreferenceからrequest-local artifactを構成する。矢印の方向はexplicit reference constructionのみを表す。時間順、semantic trend、risk aggregation、authentication aggregation、Runtime continuation、canonical historyを意味しない。

v4.0.0ではhierarchyをWで停止する。これは意図的なconsolidation boundaryである。別のcontainer typeを定義できるという理由だけで、追加levelを増やしていない。

### 6.3 Consolidation

Inspection implementationには、dedicated router、checked-in workflow test group、architecture index、canonical JSONのUTF-8 byte sizeを測定する小さなpure validation utilityが含まれる。一方で、universal Inspection engine、generic contract registry、generic identifier validator、shared semantic model、automatic hierarchy generationは導入していない。

## 7. Consumer BoundaryとGyroAuth Isolation

GyroAuthはGyroOS outputの外部consumerである。GyroOS Runtimeの実装境界には含まれない。

```text
GyroOSは明示的なRuntimeおよびInspection outputを提供できる。
GyroAuthはそれらを利用できる。
GyroOSはGyroAuth semanticsをimportしない。
Inspection resultはGyroOS内部のauthentication decisionにならない。
```

このlayer directionは、project ruleである次を保持する。

```text
Gyro Logic → GyroOS → GyroAuth
```

下位の実装層は、上位の応用層へ依存しない。

## 8. 検証

検証は、Runtime hardening、vNext Core、vNext Inspectionのchecked-in test groupによって整理されている。workflowは、bounded Runtimeおよびproduction-hardening test、route-boundary test、Inspection modelおよびservice test、utility test、PoC artifact generation、artifact count verification、artifact uploadを対象とする。

最終Inspection consolidation sequenceは、v4.0.0 Release前にGitHub Actionsを通過した。検証済みboundaryには次が含まれる。

```text
F–Wの全Inspection pathが登録されている
Inspection routeはPOST-onlyである
Inspection GET、PUT、PATCH、DELETE contractを導入していない
Runtimeおよびlayer isolationを保持している
canonical Runtime persistenceを変更していない
GyroOSはGyroAuthから独立している
```

必要であれば、正確なworkflow run identifierとtest countを投稿metadata appendixへ追加する。ただし、本稿のarchitecture上の主張は、test countだけを理論的妥当性の根拠として扱わない。

## 9. 考察

### 9.1 Trajectory Continuityのために何を保持するか

有限資源上のcontinuityは、未定義な情報全体を保持することを要求しない。後続observerが、一つの可変なlatest stateからcontinuityを再構成しなくてもよいだけの、明示的なRuntime relationを保持することが必要である。GyroOS v4.0.0では、bounded Process record、current-scope reference、Trajectory relation、Memory record、およびcanonical artifactとderived artifactの区別を保持する。

### 9.2 Canonical Ownershipが必要な理由

canonical ownershipがなければ、projectionやinspectionが、調査対象であるRuntime evidenceそのものを書き換え得る。Runtime boundaryにcanonical ownershipを固定することで、複数のderived viewを許容しながら、特定のderived interpretationをauthoritative stateへ昇格させずに済む。

### 9.3 ProjectionをNon-Canonicalに保つ理由

projectionは、利用可能なRuntime outputの一部を選び、整理するから有用である。そのselectionは、利用可能なRuntime outputに対する一つのSliceである。projection resultをcanonical historyとして扱うと、sourceとviewの区別が失われる。

### 9.4 Explicit Referenceが必要な理由

explicit referenceはhidden reconstructionを防ぐ。request-local Inspection artifactは、何が与えられ、何を参照したかを記録する。presumed latest objectを暗黙にqueryしたり、repository stateから欠落relationを推定したりしない。

### 9.5 HierarchyをWで停止した理由

F–W hierarchyは、Runtime mutationやsemantic aggregationを導入せずに、explicit Inspection artifactを多段階で構成できることを示した。しかし、別のwrapperを追加するだけでは、新しいarchitecture principleは成立しない。したがって、v4.0.0ではexpansion phaseを終了し、maintenanceおよびconsumer-driven evolutionへ移行する。

## 10. 制約

GyroOS v4.0.0には次の明示的制約がある。

```text
single-host implementation
SQLite-backed canonical repository
no distributed consensus
no multi-node Runtime continuity
experimental vNext projection and Inspection contracts
no public deployment readiness claim
no complete mathematical proof of Gyro Logic
no semantic aggregation
no risk aggregation
no authentication aggregation inside GyroOS
```

architecture figureはoverviewであり、詳細なendpoint、model、repository、operation documentationの代替ではない。

## 11. 結論

GyroOS v4.0.0は、すべてのderived informationをRuntime stateとして扱うことなく、不変のGyro Logic Coreを有限な計算資源上へ実装できることを示す。中心となる仕組みはarchitecture separationである。bounded executionは1回のProcess operationを所有する。canonical persistenceはRuntime recordとhistoryを所有する。read-only projectionは、明示的Runtime outputを変更せずに整理する。Inspectionは、explicit referenceを用いてrequest-localかつnon-canonicalなartifactを生成する。GyroAuthなどの外部consumerは、それらのoutputをGyroOS boundaryの外側で解釈する。

本設計は、完全な理解や情報全体の保存を主張しない。source、view、inspection、consumer decisionを一つのstateへ折り畳まずに、Runtime continuityを保持する有限実装規律を定義する。

## 図1

![GyroOS システム構成図・フロー図](../figures/gyroos_system_architecture_flow_jp.svg)

**図1.** GyroOSのシステム構成とbounded information flow。Gyro LogicはStructure–Slice–Stabilityの不変順序を定義し、GyroOS Runtimeはbounded executionとcanonicalなRuntime記録を所有する。vNext projectionおよびInspection contractはread-onlyかつnon-canonicalに保たれ、GyroAuthは明示的consumerとしてGyroOS実装境界の外側に位置付けられる。

## SoftwareおよびArchive

- Software Release：`GyroOS v4.0.0`
- Source Repository：`https://github.com/gitGyro-Dev/gyroos`
- Archive：`https://zenodo.org/records/21641158`
- Zenodo Record Identifier：`21641158`

## AI利用に関する著者声明

生成AIを、原稿作成支援、言語調整、構造レビュー、実装支援に使用した。著者は、定義、architecture上の主張、実装境界、code、figure、最終原稿内容を確認し、その全責任を負う。

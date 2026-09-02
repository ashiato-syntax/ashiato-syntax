[English](./README.md) | 日本語

# Ashiato Syntax

**位置と時間を宣言的に表現するための、軽量で決定論的な Syntax。**

`⟦as:1,g:9q8yyk,d:0101,t:uo-a0⟧` のような短い文字列だけで、「特定の場所・特定の期間・特定の曜日・特定の時間帯」という条件を、テキストの中に埋め込んで表現できます。

> **Status:** Draft / v1.0 Freeze Candidate
> 仕様はまだ Freeze 前の Draft 段階です。破壊的変更が入る可能性があります。

---

## これは何か

Ashiato Syntax は、次のような場面で使うことを想定した、位置情報・時間条件のための小さなテキストシンタックスです。

- SNS投稿やメッセージの中に「この場所・この時間だけ見える／有効になる」条件を埋め込む
- 位置と時間をトリガーにしたゲーム的な仕掛け（footprint / 足跡）
- QRコードやURLに埋め込んで、期間限定・場所限定のコンテンツを配布する
- 特定のサービス、イベント、企画、プロジェクトなどの利用コンテキストに投稿を紐付ける

Ashiato という名前は日本語の「足跡」に由来します。

### 例

```text
⟦as:1,g:9q8yyk⟧
```

これは、Geohash Cell `9q8yyk` にいることを表す最小構成です。

```text
⟦as:1,g:9q8yyk,z:+f0,d:0101,w:67,t:uo-a0⟧
```

これは、次の条件をすべて満たすときに Active になります。

- `9q8yyk` の Geohash Cell 内である
- UTC+09:00 のローカル時間で
- 1月1日 かつ
- 土曜日または日曜日 かつ
- 18:00〜翌06:00 の時間帯

## Application Context

`c` フィールドを指定することで、Ashiato を特定の **Application Context** に関連付けることができます。

Application Context は、例えば次のような単位で利用できます。

- 特定のサービス
- 特定のイベント
- 特定の企画・キャンペーン
- 特定のプロジェクト

`c` は **opaque identifier（不透明な識別子）** です。Ashiato Syntax は、`c` の生成方法や意味を規定しません。

`c` の値には `0-9` と `a-z` のみを使用し、長さは **1〜22文字**です。UUID を使用することもできますが、UUID は必須ではありません。

Ashiato Syntax 自体は Application Context の登録・発行・予約・グローバル管理を行いません。イベント主催者やサービス提供者などが、それぞれ独立して `c` を生成できます。必要な範囲での衝突回避は、利用側の責務です。

`c` を省略した場合は、特定の Application Context に紐付かない **汎用 Ashiato** として扱います。

例：

```text
⟦as:1,g:9q8yyk,d:0101⟧
```

```text
⟦as:1,c:7k3m9x,g:9q8yyk,d:0101⟧
```

詳細な仕様は、Application Context Field (`c`) の仕様を参照してください。

## 設計方針

- **単純な論理モデル**：Field 間は AND、同一 Field 内の複数値は OR。任意の Boolean 式や括弧はサポートしない。
- **Syntax と Semantics の分離**：ABNF による構文検証と、Semantic Validation（値の妥当性検証）を明確に分ける。
- **決定論的な Canonical Form**：同じ意味の Ashiato は必ず同じ Canonical String に正規化される（Idempotence / Semantic Preservation / Determinism を保証）。
- **拡張可能**：`x-<namespace>-<name>` 形式の Extension Field により、標準仕様を壊さずに独自フィールドを追加できる。
- **コンテキスト対応と非中央集権性**: Application Contextによってサービス、イベント、企画などを区別しつつ、中央集権的な登録管理を必要としない。

## 発見方法について

Ashiato Syntax 自体は、SNS 上に投稿された Ashiato の発見方法を規定しません。
各サービスは、ハッシュタグ、メタデータ、API、その他の方法を独自に用いて
Ashiato Syntax を含む投稿を発見・処理できます。

Ashi@ では、対応 SNS 上で Ashiato Syntax を含む投稿を発見するため、
`#Ashiato` ハッシュタグを使用します。
`#Ashiato` は Ashiato Syntax 自体の仕様ではなく、Ashi@ における
発見方式の一部です。

## セキュリティとプライバシーに関する留意事項

Ashiato Syntax は、位置情報および時間情報を含む情報をSNS等の公開された場所で共有するために使用される場合があります。実装者および利用者は、以下の事項に注意してください。

### 1. プライバシーに関する留意事項

位置情報および時間情報を公開することにより、個人の居場所、行動、生活圏、その他の個人情報が第三者によって推測される可能性があります。

SNS等に公開されたAshiato Syntaxは、第三者によって取得・解析・保存され得ます。また、複数の投稿を組み合わせることにより、単一の投稿からは明らかでない行動パターンや生活圏等が推測される可能性があります。

位置情報や時間情報を公開する際は、公開によって生じ得るプライバシー上のリスクを十分に考慮してください。

### 2. 位置情報の精度

必要以上に高精度な位置情報を公開しないことを推奨します。

特に、自宅、勤務先、学校、その他の継続的に滞在する場所については、高精度な位置情報を公開することで、個人の生活圏や所在地が推測される可能性があります。

Ashiato Syntax は、特定の位置精度や精度の丸め方を要求しません。位置情報の精度、表示範囲、公開方法等は、Ashiato Syntaxを利用するサービスのポリシーおよび利用者の判断に委ねられます。

### 3. `x-*` 拡張フィールド

`x-*` 拡張フィールドは、サービスまたは実装固有の情報を格納するために使用できます。

これらのフィールドの意味および利用方法は、Ashiato Syntaxの標準仕様では規定されません。

例えば、Ashiato Syntaxを利用するサービスは、投稿やSyntaxの発行を識別するためのサービス固有のIDを `x-*` 拡張フィールドに格納できます。

実装者は、`x-*` 拡張フィールドに個人情報その他の機微な情報を含める場合、その情報が第三者によって取得・解析され得ることを考慮してください。

### 4. サービスによる安全対策

Ashiato Syntaxを利用するサービスは、位置情報および時間情報の性質を考慮し、適切なセキュリティおよびプライバシー対策を講じることが推奨されます。

これには、例えば以下が含まれます。

* 位置情報の精度を制限または丸める
* 投稿または位置情報の公開を遅延させる
* 検索および発見可能性を制限する
* 複数の投稿から行動履歴や生活圏を推測される可能性を考慮する
* 不正な投稿や自動化された大量投稿等を防止する

これらの対策はAshiato Syntax自体の必須要件ではなく、Ashiato Syntaxを利用するサービスが、その用途および利用環境に応じて実装するものです。

### 5. 現地に存在したことを証明するものではない

Ashiato Syntaxに位置情報が記載されていることは、そのSyntaxを生成または投稿した人物が、記載された地点に実際に存在したことを証明するものではありません。

Ashiato Syntaxは、位置情報を記述するための構文であり、位置情報の取得方法、取得時の本人確認、現地での存在確認その他のProof of Presence（現地存在証明）を規定しません。

現地に存在したことを要求または検証するかどうか、およびその方法は、Ashiato Syntaxを利用するサービスまたは実装の責務です。

## 仕様書

完全な仕様は以下を参照してください。

- [Ashiato Syntax v1.0 — (日本語仕様書)](./Ashiato_Syntax_v1_0_JP.md)
- [Ashiato Syntax v1.0 — (English Specification)](./Ashiato_Syntax_v1_0_EN.md)

仕様書には ABNF Grammar、Semantic Validation ルール、Canonicalization ルール、Reference Evaluation Algorithm、および Test Vectors 一式を含みます。

## Non-Goals（v1.0 では扱わないもの）

Ashiato Syntax はあくまで位置・時間条件を表現するための Syntax であり、以下は仕様化しません。実装（アプリケーション側）の責務です。

- 距離計算・発見半径・GPS Accuracy
- Ownership / Claim / Score / Cooldown / Anti-Cheat などのゲームメカニクス
- Server API / Database Schema / SNS API
- 任意の Boolean Expression
- Application Contextの発行・登録・管理

詳細は仕様書の「Non-Goals」セクションを参照してください。

## Test Vectors

仕様書内の Test Vectors（境界値・Canonicalization・エラーケースを含む）は、各言語での実装の適合性検証にそのまま利用できます。

## Contributing

Issue や Pull Request は歓迎します。特に以下のフィードバックを歓迎します。

- 仕様上の曖昧さ・矛盾の指摘
- 各言語（TypeScript, Rust, Go, Python など）でのリファレンス実装
- Test Vectors の追加

v1.0 は Freeze Candidate のため、後方互換性を壊す変更提案は Issue でまず議論してください。

## License

Ashiato Syntaxの仕様書およびドキュメントは、Creative Commons Attribution 4.0 International（CC BY 4.0）ライセンスで公開されています。

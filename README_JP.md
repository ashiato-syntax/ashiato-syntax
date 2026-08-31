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

## 設計方針

- **単純な論理モデル**：Field 間は AND、同一 Field 内の複数値は OR。任意の Boolean 式や括弧はサポートしない。
- **Syntax と Semantics の分離**：ABNF による構文検証と、Semantic Validation（値の妥当性検証）を明確に分ける。
- **決定的な Canonical Form**：同じ意味の Ashiato は必ず同じ Canonical String に正規化される（Idempotence / Semantic Preservation / Determinism を保証）。
- **拡張可能**：`x-<namespace>-<name>` 形式の Extension Field により、標準仕様を壊さずに独自フィールドを追加できる。
- **タイムゾーンに依存しない**：IANA Time Zone や DST は扱わず、固定 UTC Offset のみを扱う。

## 仕様書

完全な仕様は以下を参照してください。

- [Ashiato Syntax v1.0 — （日本語仕様書）](./Ashiato_Syntax_v1_0_JP.md)
- [Ashiato Syntax v1.0 — （English Specification）](./Ashiato_Syntax_v1_0_EN.md)

仕様書には ABNF Grammar、Semantic Validation ルール、Canonicalization ルール、Reference Evaluation Algorithm、および Test Vectors 一式を含みます。

## Non-Goals（v1.0 では扱わないもの）

Ashiato Syntax はあくまで位置・時間条件を表現するための Syntax であり、以下は仕様化しません。実装（アプリケーション側）の責務です。

- 距離計算・発見半径・GPS Accuracy
- Ownership / Claim / Score / Cooldown / Anti-Cheat などのゲームメカニクス
- Server API / Database Schema / SNS API
- IANA Time Zone・DST Rule
- 任意の Boolean Expression

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

TBD

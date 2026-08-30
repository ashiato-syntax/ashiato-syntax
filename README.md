# Ashiato Syntax Specification

**Version:** 1.0
**Status:** Draft

---

## 1. 概要

Ashiato Syntax は、SNSの投稿本文に位置情報と時間条件を埋め込むための軽量なマイクロシンタックスである。

Ashiato Syntax自体は特定のSNS、サービス、プロトコルに依存しない。

Misskey、Bluesky、Mastodonなど、投稿本文に任意の文字列を含められるサービスで利用できる。

Ashiato Syntaxは暗号化された位置情報ではない。`g` に含まれる位置情報は公開情報であり、第三者が復元できることを前提とする。

Ashiato Syntaxが表現するのは主に以下の情報である。

* **どこ**にあるか
* **いつから**有効か
* **いつまで**有効か
* **何月何日**に有効か
* **何曜日**に有効か
* **何時から何時まで**有効か

Ashiatoの「発見距離」やゲームルールなどはSyntaxの仕様外とし、利用するクライアントに委ねる。

---

# 2. 基本構文

Ashiato Syntax v1の基本形は以下の通り。

```text
⟦as:1,g:<geohash>[,<field>:<value>...]⟧
```

`as` と `g` は必須であり、順序も固定する。

```text
as → g
```

`g` 以降のフィールドは任意であり、**順序は自由**とする。

現在定義されているフィールド：

| Field | 意味                |
| ----- | ----------------- |
| `g`   | Location          |
| `s`   | Start Time        |
| `e`   | Expiration Time   |
| `d`   | Date Condition    |
| `w`   | Weekday Condition |
| `t`   | Time Condition    |

---

# 3. Version

Ashiato Syntaxのバージョンは `as` フィールドで指定する。

v1では、

```text
as:1
```

のみを定義する。

例えば、

```text
⟦as:1,g:9q8yyk⟧
```

はAshiato Syntax Version 1を意味する。

未知のバージョンについては、そのバージョンの仕様を理解していない実装は解釈してはならない。

例えばv1実装が、

```text
⟦as:2,g:9q8yyk⟧
```

を取得した場合、Version 2固有の意味を推測してはならない。

---

# 4. Field Ordering

## 4.1 Parsing

パーサーは `g` より後のフィールドについて、**任意の順序を受け付けなければならない**。

以下は同じ意味を持つ。

```text
⟦as:1,g:9q8yyk,s:abc,e:def,w:67,t:uo-a0⟧
```

```text
⟦as:1,g:9q8yyk,t:uo-a0,w:67,e:def,s:abc⟧
```

パーサーはフィールドの順序に依存してはならない。

## 4.2 Generation

Ashiato Syntaxを生成する実装は、以下の正規順序を使用することを推奨する。

```text
as → g → s → e → d → w → t
```

存在しない任意フィールドは省略する。

この順序は**生成時の正規形**であり、パーサーがこの順序を要求するものではない。

正規形を定義することで、将来的なハッシュ、署名、キャッシュ、重複排除などへの利用を容易にする。

## 4.3 Duplicate Fields

同一キーを1つのAshiato Syntax内に複数回記述してはならない。

不正：

```text
⟦as:1,g:9q8yyk,w:67,w:135⟧
```

複数の値を指定する必要がある場合は、各フィールドで定義された複数値形式を使用する。

---

# 5. Character Encoding

Ashiato Syntaxの構文部分にはASCII文字を使用し、開始・終了デリミタには以下のUnicode文字を使用する。

```text
⟦  U+27E6 MATHEMATICAL LEFT WHITE SQUARE BRACKET
⟧  U+27E7 MATHEMATICAL RIGHT WHITE SQUARE BRACKET
```

構文全体はUTF-8で表現する。

デリミタはUnicode normalizationによって別の文字へ変換してはならない。

## 5.1 区切り文字

| 文字  | 用途               |
| --- | ---------------- |
| `,` | フィールド間の区切り       |
| `.` | 同一フィールド内の複数値の区切り |
| `-` | 時間範囲の開始・終了       |
| `:` | キーと値の区切り         |

---

# 6. Base36 Encoding

`s`、`e`、`t` の値のエンコードにはBase36を使用する。

## 6.1 Alphabet

Ashiato Syntax v1では以下の文字セットを使用する。

```text
0123456789abcdefghijklmnopqrstuvwxyz
```

数字 `0-9` と小文字英字 `a-z` のみを使用する。

大文字英字は正規形ではない。

## 6.2 Leading Zero

Base36値の先頭に不要な `0` を付加しない。

例えば10進数35は、

```text
z
```

と表現する。

以下は正規形ではない。

```text
0z
00z
```

0そのものは、

```text
0
```

と表現する。

実装は入力解析時に大文字を受け入れてもよいが、生成およびCanonicalizationでは小文字を使用する。

---

# 7. Location

## 7.1 `g`

位置情報を示す。

値には標準的な **Geohash** を使用する。

```text
g:9q8yyk
```

`g` は必須であり、`as` の直後に置く。

Ashiato Syntaxは独自の緯度・経度エンコード方式を定義しない。

## 7.2 Geohash Character Set

`g` の値には、標準的なGeohashで使用されるBase32 alphabetを使用する。

```text
0123456789bcdefghjkmnpqrstuvwxyz
```

以下の文字は使用しない。

```text
a
i
l
o
```

Geohashは小文字のみを正規形とする。

## 7.3 精度

Geohashの文字数によって公開位置の精度を選択できる。

以下は目安であり、実際のセルサイズは緯度によって変化する。

| Length | おおよその精度 |
| -----: | ------- |
|      5 | 数km級    |
|      6 | 1km級    |
|      7 | 100m級   |
|      8 | 数十m級    |
|      9 | 数m級     |
|     10 | 1m級     |

投稿者は、公開したい位置精度に応じてGeohashの文字数を選択する。

## 7.4 位置情報の公開

`g` は暗号化されない。

Geohashをデコードすることで、公開された位置セルを取得できる。

Ashiato Syntaxでは位置情報の秘匿を目的とせず、**投稿者が公開位置の精度を選択できること**を基本方針とする。

---

# 8. Time Zone

Ashiato Syntax v1では、時間条件の解釈に使用するタイムゾーンを**UTCに固定する**。

対象となるフィールド：

```text
s
e
d
w
t
```

したがって、`d`、`w`、`t` は投稿地点のローカルタイムではなく、UTCを基準として評価する。

## 8.1 理由

AshiatoではGeohashの精度を投稿者が任意に選択できる。

Geohashからタイムゾーンを推定すると、位置精度と時間条件が暗黙に結びついてしまう。

また、タイムゾーン境界付近では1つのGeohashセルが複数のタイムゾーンにまたがる可能性がある。

そのためv1では、解釈が一意になるUTCを採用する。

## 8.2 将来の拡張

将来的にローカルタイムを扱う必要が生じた場合は、拡張フィールドによってタイムゾーンを指定できるようにする可能性がある。

v1ではタイムゾーン指定フィールドを定義しない。

---

# 9. Start Time

## `s`

Ashiatoが有効になる絶対時刻を指定する。

値は以下の手順でエンコードする。

1. Unix timestampを取得する
2. 60で割って切り捨てる
3. Base36へ変換する

定義：

```text
s = Base36(floor(unix_timestamp / 60))
```

精度は1分。

`s` は任意。

## 9.1 Semantic Range

Base36をデコードした値は、**非負のUnix minutesを表す整数**でなければならない。

---

# 10. Expiration Time

## `e`

Ashiatoが無効になる絶対時刻を指定する。

エンコード方式は `s` と同じ。

```text
e = Base36(floor(unix_timestamp / 60))
```

精度は1分。

`e` は任意。

## 10.1 Semantic Range

Base36をデコードした値は、非負のUnix minutesを表す整数でなければならない。

## 10.2 `s` と `e`

両方指定された場合、

```text
s <= current_minute <= e
```

を満たす期間のみAshiatoを有効とする。

`s` のみの場合は指定時刻以降に有効。

`e` のみの場合は指定時刻まで有効。

---

# 11. Date Condition

## `d`

毎年繰り返される特定の月日を指定する。

形式：

```text
d:<MMDD>[.<MMDD>...]
```

1つ以上の月日を指定できる。

複数の月日は `.` で区切る。

例：

```text
d:0915
```

毎年9月15日に有効。

```text
d:0101.0505
```

毎年1月1日または5月5日に有効。

```text
d:0101.0505.0915
```

毎年1月1日、5月5日、9月15日に有効。

## 11.1 Month-Day Validity

各値は4桁の `MMDD` で表現する。

値は有効なGregorian calendarの月日を表さなければならない。

例えば以下は不正：

```text
0000
1332
0231
```

`0229` は許可する。

`0229` は、評価対象となる年が閏年でない場合、その年には条件を満たさないものとして扱う。

## 11.2 複数指定

同一の月日を複数回指定してはならない。

複数の月日は昇順に記述する。

正規形：

```text
d:0101.0505.0915
```

パーサーは入力時に順序を問わず受け入れてもよいが、Canonicalizationでは昇順に並べる。

## 11.3 年の扱い

`d` は年を指定しない。

指定された月日は**毎年繰り返される条件**として扱う。

特定の年だけ有効にしたい場合は `s` / `e` を使用する。

---

# 12. Weekday Condition

## `w`

曜日を指定する。

```text
1 = 月曜日
2 = 火曜日
3 = 水曜日
4 = 木曜日
5 = 金曜日
6 = 土曜日
7 = 日曜日
```

複数の曜日を指定する場合は数字を連結する。

例：

```text
w:135
```

月・水・金曜日。

```text
w:67
```

土・日曜日。

`w` は任意。

## 12.1 Validity

`w` の各文字は `1`〜`7` のいずれかでなければならない。

同じ曜日を複数回指定してはならない。

曜日は昇順に記述する。

`w` の値にはBase36エンコードを使用しない。

---

# 13. Time Condition

## `t`

1日の中でAshiatoが有効になる時間帯を指定する。

時刻は00:00からの経過分数として表現し、その整数をBase36へ変換する。

| 時刻    |   分数 |
| ----- | ---: |
| 00:00 |    0 |
| 00:01 |    1 |
| 01:00 |   60 |
| 06:00 |  360 |
| 12:00 |  720 |
| 18:00 | 1080 |
| 23:59 | 1439 |

形式：

```text
t:<start>-<end>
```

## 13.1 Base36

時刻のBase36表現は可変長とする。

不要な先頭の `0` は付加しない。

例：

```text
00:00 → 0
01:00 → 1o
06:00 → a0
12:00 → k0
18:00 → uo
23:59 → zz
```

## 13.2 Validity

Base36をデコードした値は、0以上1439以下の整数でなければならない。

## 13.3 境界

時間条件は半開区間 `[start, end)` とする。

```text
start <= time < end
```

終了時刻そのものは範囲に含まれない。

## 13.4 日跨ぎ

開始時刻が終了時刻より後の場合、時間帯は翌日にまたがるものとする。

```text
t:uo-a0
```

は、

```text
18:00〜翌06:00
```

を意味する。

内部的には、

```text
time >= 18:00
OR
time < 06:00
```

として評価する。

## 13.5 同一時刻

開始時刻と終了時刻が同一となる指定は使用してはならない。

24時間有効の場合は `t` を省略する。

---

# 14. Condition Semantics

Ashiatoの有効性は、現在時刻に対する複数のpredicateとして評価する。

概念的には以下のように定義する。

```text
Active(now) =
    LocationMatches
    AND StartCondition(now)
    AND ExpirationCondition(now)
    AND DateCondition(now)
    AND WeekdayCondition(now)
    AND TimeCondition(now)
```

存在しない任意フィールドの条件は常にtrueとして扱う。

## 14.1 Current Minute

`s` および `e` の評価にはUnix timestampそのものではなく、Unix minutesを使用する。

```text
current_minute = floor(current_unix_timestamp / 60)
```

したがって、

```text
s <= current_minute <= e
```

として評価する。

## 14.2 フィールド間

異なるフィールドの条件は**AND**で結合する。

例えば、

```text
d:0101,w:67,t:uo-a0
```

は、

```text
DateCondition
AND WeekdayCondition
AND TimeCondition
```

となる。

## 14.3 同一フィールド内

同一フィールド内で複数の値が指定された場合、それらは**OR**で結合する。

例えば、

```text
d:0101.0505
```

は、

```text
date == 0101
OR
date == 0505
```

となる。

```text
w:67
```

は、

```text
weekday == Saturday
OR
weekday == Sunday
```

となる。

## 14.4 複雑な論理式

Ashiato Syntax v1では、任意のOR/ANDを組み合わせた複雑な論理式はサポートしない。

条件構造は、

```text
フィールド間 → AND
フィールド内 → OR
```

に限定する。

---

# 15. Location Matching

Ashiato Syntaxは、現在地との距離をどのように判定するかを規定しない。

Syntaxが表現するのは、公開されたGeohashセルのみである。

Ashiato対応クライアントは、独自のルールで現在地との一致を判定できる。

クライアントが決定する項目の例：

* 現在位置との距離
* 発見半径
* GPS accuracy
* 位置情報へのアクセス許可
* 発見済みAshiatoの扱い
* UI
* 通知
* ゲームルール

これらはAshiato Syntax v1の仕様外とする。

このため、同一のAshiato Syntaxを、

* 現地探索ゲーム
* 地図上の口コミ
* 観光ガイド
* イベント
* 街歩き
* チェックイン

など、異なる用途で利用できる。

---

# 16. Client-side Discovery

Ashiato Syntaxは、現在地をサーバーへ送信することを要求しない。

基本的なクライアント側処理は以下のようになる。

```text
SNSから投稿を取得
        ↓
Ashiato Syntaxを抽出
        ↓
gをGeohashとして解釈
        ↓
端末の現在位置と比較
        ↓
時間条件を評価
        ↓
Ashiatoを発見
```

現在位置そのものをSNSサーバーへ送信する必要はない。

---

# 17. Unknown Fields

将来的な拡張性を確保するため、v1で定義されていない未知のフィールドを構文上許容する。

例えば、

```text
⟦as:1,g:9q8yyk,x:example⟧
```

の `x` はv1では未知のフィールドである。

v1実装は未知のフィールドを**構文上有効なものとして受け入れ、その意味を無視してよい**。

未知のフィールドの存在だけを理由としてAshiato Syntax全体を無効としてはならない。

ただし、未知フィールドをCanonicalizationする際には、後述するCanonicalization Rulesに従う。

---

# 18. Multiple Ashiato Syntax

1つの投稿本文に複数のAshiato Syntaxが存在することを許可する。

各Ashiato Syntaxは独立したAshiatoとして扱う。

例えば、

```text
本文

⟦as:1,g:aaaaaa⟧

途中

⟦as:1,g:bbbbbb⟧
```

には2つのAshiatoが存在する。

Ashiato Syntax自体は、複数のAshiatoが同一投稿に存在することによる優先順位を定義しない。

生成クライアントが通常の投稿にAshiatoを追加する場合は、1つだけ配置することを推奨する。

---

# 19. Text Extraction

Ashiato SyntaxはSNS投稿本文中の任意の位置に出現できる。

例えば以下はいずれも構文上許可される。

```text
今日はここに来た。

⟦as:1,g:9q8yyk⟧
```

```text
foo ⟦as:1,g:9q8yyk⟧ bar
```

```text
foo⟦as:1,g:9q8yyk⟧bar
```

生成クライアントは、ユーザーが投稿本文を入力する際、Ashiato Syntaxを本文末尾に配置することを推奨する。

## 19.1 Extraction Process

実装は以下の順序でAshiatoを処理することを推奨する。

```text
本文
 ↓
⟦...⟧ の候補を抽出
 ↓
Ashiato Syntaxとしてparse
 ↓
Validation
 ↓
有効なAshiatoとして扱う
```

Ashiato Syntaxは本文中の通常テキストとして扱われるため、Markdown、MFM、引用、コードブロックなどの文脈による意味はAshiato Syntax自体では定義しない。

それらを特別扱いするかどうかは各SNSまたはクライアントに委ねる。

---

# 20. Validation Rules

Ashiato Syntaxは、構文上正しいだけでなく、各フィールドの意味論上の制約を満たさなければならない。

主要な検証項目：

### Required

* `as` が存在する
* `g` が存在する
* `as` が `g` より前に存在する
* `as` が `g` の直後に存在する

### Version

* v1では `as:1` のみ解釈する

### Location

* `g` は有効なGeohashである
* Geohashは空でない

### Start / Expiration

* `s` / `e` は有効なBase36
* decoded valueは非負整数
* Unix minutesとして解釈可能

### Date

* `MMDD` が4桁
* 有効なGregorian calendarの月日
* `0229` は許可
* 同一値の重複は禁止
* Canonicalizationでは昇順

### Weekday

* 各文字が `1`〜`7`
* 重複禁止
* 昇順

### Time

* decoded valueが0〜1439
* `start == end` は禁止
* `start` / `end` は整数

### Duplicate Fields

* 同一フィールドの重複は禁止

未知フィールドについては、v1で定義されていなくても構文上許容する。

---

# 21. Canonicalization

Ashiato Syntaxは、意味的に同一の表現を一意の正規形へ変換できることを目指す。

Canonicalizationは以下の規則に従う。

## 21.1 Field Order

以下の順序に並べる。

```text
as → g → s → e → d → w → t → extension fields
```

未知のextension fieldは、キーの辞書順で並べる。

## 21.2 Base36

`s`、`e`、`t` のBase36値は、

* 小文字
* 不要な先頭 `0` を除去

とする。

## 21.3 Geohash

`g` は小文字にする。

## 21.4 Date

`d` の複数値は昇順に並べる。

## 21.5 Weekday

`w` の複数値は昇順に並べる。

## 21.6 Extension Fields

未知フィールドはキーの辞書順で並べる。

未知フィールドの値について、v1では独自の意味論的正規化を行わない。

## 21.7 Canonical Example

以下：

```text
⟦as:1,g:9q8yyk,t:uo-a0,w:67⟧
```

はCanonicalizationによって、

```text
⟦as:1,g:9q8yyk,w:67,t:uo-a0⟧
```

となる。

---

# 22. Security and Privacy Considerations

## 22.1 Location is Public

`g` は公開情報である。

Ashiato Syntaxは位置情報の秘匿や匿名化を提供しない。

投稿者は、公開してよい位置精度を選択する必要がある。

## 22.2 Geohash Precision

Geohashの文字数を増やすほど公開位置は詳細になる。

クライアントは、ユーザーが位置精度を明示的に選択できるUIを提供することが望ましい。

## 22.3 Rainbow Tables

Geohashは秘密情報ではないため、Geohash値に対する辞書攻撃や事前計算を防ぐことはAshiato Syntax v1の目的としない。

Ashiato Syntaxは、

> **「位置情報を隠す」のではなく、「公開位置を意図的な精度で共有する」**

という設計思想を採用する。

## 22.4 Spoofing

Ashiato Syntax単体では、投稿者が実際にその場所にいたことを暗号学的に証明しない。

第三者は任意のAshiato Syntaxを生成できる。

したがって、

> 「現地に行ったことを証明する」

ことはAshiato Syntax v1の機能ではない。

現地探索ゲームなどで必要となる不正対策は、各クライアントまたはサービス側で実装する。

## 22.5 Client-side Location

Ashiato対応クライアントは、現在位置をサーバーへ送信せずにAshiatoを発見できる設計を推奨する。

---

# 23. Reference Processing Model

Ashiato対応クライアントは、概念的に以下の処理を行う。

```text
1. SNSから投稿を取得
        ↓
2. 本文からAshiato Syntaxを抽出
        ↓
3. Syntaxをparse
        ↓
4. Validation
        ↓
5. gをGeohashとして解釈
        ↓
6. 現在位置との関係をクライアント独自ルールで評価
        ↓
7. s/e/d/w/tを評価
        ↓
8. 有効なAshiatoをUIへ表示
```

位置判定と時間判定の結果がともに有効である場合、クライアントはAshiatoを「発見可能」として扱える。

---

# 24. ABNF

Ashiato Syntax v1の基本的な文法を以下のABNFで定義する。

```abnf
ashiato = "⟦" "as:1" "," "g:" geohash *("," field) "⟧"

field = start-field
      / expiration-field
      / date-field
      / weekday-field
      / time-field
      / extension-field

start-field = "s:" base36
expiration-field = "e:" base36
date-field = "d:" month-day *("." month-day)
weekday-field = "w:" weekday-value
time-field = "t:" base36 "-" base36

month-day = 4DIGIT
weekday-value = 1*7DIGIT
base36 = 1*(DIGIT / %x61-7A)

geohash = 1*(%x30-39 / %x62-68 / %x6A-6B / %x6D-6E / %x70-7A)

extension-field = extension-key ":" extension-value
extension-key = 1*(ALPHA / DIGIT)
extension-value = 1*(ALPHA / DIGIT / "." / "-")
```

ABNFは構文上の構造を定義する。

月日の妥当性、曜日の範囲、Base36値の範囲、時間範囲などはValidation Rulesおよび各フィールドの意味論に従う。

---

# 25. Examples

## 25.1 Basic

```text
⟦as:1,g:9q8yyk⟧
```

指定された場所に恒久的なAshiatoを残す。

## 25.2 Future Activation

```text
⟦as:1,g:9q8yyk,s:xxxxx⟧
```

指定された絶対時刻から有効。

## 25.3 Expiration

```text
⟦as:1,g:9q8yyk,e:xxxxx⟧
```

指定された絶対時刻まで有効。

## 25.4 Multiple Dates

```text
⟦as:1,g:9q8yyk,d:0101.0505.0915⟧
```

毎年1月1日、5月5日、9月15日に有効。

## 25.5 Weekday

```text
⟦as:1,g:9q8yyk,w:67⟧
```

毎週土曜日・日曜日に有効。

## 25.6 Time

```text
⟦as:1,g:9q8yyk,t:uo-a0⟧
```

毎日18:00〜翌06:00に有効。

## 25.7 Combined

```text
⟦as:1,g:9q8yyk,s:xxxxx,e:xxxxx,d:0101.0505,w:67,t:uo-a0⟧
```

指定された期間内で、

* 1月1日または5月5日
* 土曜日または日曜日
* 18:00〜翌06:00

のすべてを満たす場合に有効。

## 25.8 Multiple Ashiato

```text
今日はこの街を歩いてきた。

⟦as:1,g:9q8yyk⟧

このあと別の場所にも行く。

⟦as:1,g:9q8z0p⟧
```

1つの投稿に2つの独立したAshiatoが存在する。

---

# 26. Design Principles

Ashiato Syntax v1は以下を基本方針とする。

1. **SNS非依存**
2. **サーバー非依存**
3. **特定のSNS APIに依存しない**
4. **既存の標準技術を最大限利用する**
5. **短い文字列で表現する**
6. **位置情報は暗号化しない**
7. **投稿者が公開位置の精度を選択できる**
8. **時間条件を1分単位で指定できる**
9. **第三者が容易に実装できる**
10. **未知の拡張に対応できる**
11. **ゲーム固有のルールをSyntaxに持ち込まない**
12. **`as` と `g` を先頭に固定する**
13. **`g` 以降のフィールドは順序に依存しない**
14. **フィールド間はAND、同一フィールド内はORとする**
15. **時間条件はUTCで評価する**
16. **複雑な論理式をサポートせず、仕様を小さく保つ**
17. **位置の真正性を暗号学的に保証しない**
18. **投稿本文に埋め込めるポータブルな形式とする**

---

# 27. Scope of v1

Ashiato Syntax v1は、以下のみを標準化する。

```text
Location
    ↓
    g

Absolute Time
    ↓
    s / e

Recurring Date
    ↓
    d

Recurring Weekday
    ↓
    w

Recurring Time
    ↓
    t
```

以下はv1の仕様外とする。

* 発見半径
* GPS精度
* 現地訪問証明
* 暗号化
* 投稿者認証
* タイムゾーン指定
* 高度
* 方角
* 移動速度
* ゲームルール
* UI
* 通知
* サーバー側位置検索
* 特定SNSのAPI仕様

Ashiato Syntaxは、

> **「どこに、いつから、いつまで、どの月日・曜日・時間帯に有効なAshiatoなのか」**

を記述するための、SNS非依存の最小限の共通フォーマットを目指す。

# Ashiato Syntax v1.0
## 日本語仕様書

**Status:** Draft / v1.0 Freeze Candidate

---

## 1. 概要

Ashiato Syntax は、SNSなどの既存のテキスト環境にそのまま埋め込むことができる、位置・時間条件を表現するための軽量な Micro-Syntax である。

Ashiato Syntax は、以下の情報を1つの文字列として表現する。

- 地理的位置
- 固定 UTC Offset
- 絶対的な有効期間
- 月日による周期条件
- 曜日による周期条件
- 時刻による周期条件
- 将来拡張のための Extension Field

Ashiato Syntax 自体は、以下を定義しない。

- 現在位置との距離判定
- GPS 精度
- 発見半径
- ゲームルール
- スコア
- 所有権
- クールダウン
- サーバー側の位置情報処理
- SNS の機能や挙動

基本的な設計思想は次の通りである。

```text
Ashiato Syntax
    ├─ Location
    ├─ Absolute Time
    └─ Recurring Local Time

Client / Application
    ├─ Location Matching
    ├─ Discovery Radius
    ├─ GPS Accuracy
    ├─ UI / UX
    └─ Game Rules
```

Ashiato Syntax は「条件の記述」を担当し、その条件をどのような体験に変換するかはクライアントまたはアプリケーションに委ねる。

---

# 2. 基本形式

Ashiato Syntax は、以下の Unicode 区切り文字で囲まれる。

```text
⟦ ... ⟧
```

基本形は次の通り。

```text
⟦as:1,g:<geohash>[,<field>...]⟧
```

例：

```text
⟦as:1,g:9q8yyk⟧
```

---

# 3. 固定ヘッダー

Ashiato Syntax v1.0 の先頭には、以下の固定ヘッダーを必ず持つ。

```text
as:1
```

`as:1` は Ashiato Syntax の Major Version 1 を示す。

`as:1` と `g:<geohash>` は固定ヘッダーとして扱う。

```text
⟦
  as:1
  ,
  g:<geohash>
  ,
  ...
⟧
```

`as` と `g` は必須であり、順序は固定である。

---

# 4. Field の論理モデル

Ashiato Syntax の論理構造は非常に単純である。

```text
Active = AND(fields)

Field = OR(values)
```

つまり、

- Field 間は AND
- 同一 Field 内の複数 Value は OR

である。

例えば、

```text
d:0101.0505,w:67
```

は、

```text
(1月1日 OR 5月5日)
AND
(土曜日 OR 日曜日)
```

を意味する。

したがって、

```text
d:0101.0505,w:67,t:uo-a0
```

は、

```text
(1月1日 OR 5月5日)
AND
(土曜日 OR 日曜日)
AND
(18:00〜06:00)
```

である。

Ashiato Syntax v1.0 は、任意の Boolean Expression や括弧付き論理式をサポートしない。

---

# 5. Location Field: g

## 5.1 形式

```text
g:<geohash>
```

`g` は標準的な Geohash を使用する。

例：

```text
g:9q8yyk
```

Geohash は、特定の一点ではなく**Geohash Cell**を表す。

したがって、

```text
g:9q8yyk
```

は「その Geohash Cell」を意味し、正確な座標一点を意味しない。

---

## 5.2 Geohash の仕様

Ashiato Syntax は独自の緯度・経度エンコード方式を定義しない。

`g` の解釈は、標準的な Geohash の仕様に従う。

Geohash の alphabet は以下である。

```text
0123456789bcdefghjkmnpqrstuvwxyz
```

大文字は使用しない。

---

## 5.3 Geohash Length

v1.0 では Geohash の長さは、

```text
1〜12文字
```

とする。

Geohash の長さは Syntax Grammar ではなく Semantic Validation によって検証する。

概算の Cell Size は次の通りである。

| Length | おおよその Cell Size |
|---:|---:|
| 5 | 数 km 級 |
| 6 | 1 km 級 |
| 7 | 100 m 級 |
| 8 | 数十 m 級 |
| 9 | 数 m 級 |
| 10 | 1 m 級 |

これは概算値であり、緯度によって実際の Cell Dimensions は変化する。

---

## 5.4 Distance Matching

Ashiato Syntax は、`g` と現在位置との距離判定方法を規定しない。

例えばクライアントは、

- 現在位置が Geohash Cell 内にある
- Cell との距離が一定以内
- Cell Center との距離が一定以内
- GPS 精度を考慮した独自判定

などを採用できる。

これらはすべて Client / Application の責務である。

---

# 6. UTC Offset Field: z

## 6.1 形式

```text
z:<signed-base36>
```

`z` は固定 UTC Offset を分単位で表現する。

`z` は IANA Time Zone ではない。

例えば、

```text
z:+f0
```

は、

```text
UTC+09:00
```

を意味する。

`Asia/Tokyo` のような Time Zone Identifier は使用しない。

---

## 6.2 Fixed UTC Offset

`z` は評価時点に応じて変化する Time Zone ではなく、固定値である。

したがって、

```text
z:+f0
```

は常に UTC+09:00 を意味する。

DST や政治的な Time Zone Rule は適用しない。

---

## 6.3 値の範囲

v1.0 では、

```text
-1440 <= z <= +1440
```

を許可する。

これは IANA Time Zone や ISO 8601 の Time Zone Offset の完全な互換表現を意味しない。

Ashiato v1.0 における `z` は、**固定分単位の UTC Offset**として定義される独自の値である。

---

## 6.4 Signed Base36

`z` は signed Base36 で表現する。

- 正数 → `+`
- 負数 → `-`
- 0 → 符号なし

例：

```text
0     → 0
540   → +f0
-300  → -8c
```

`+0` および `-0` は構文上受理してよいが、Semantic Value は 0 とする。

Canonical Form では 0 の `z` は省略する。

---

## 6.5 デフォルト値

`z` が省略された場合、その値は `0` とする。

したがって、

```text
⟦as:1,g:9q8yyk⟧
```

と、

```text
⟦as:1,g:9q8yyk,z:0⟧
```

は意味的に同値である。

Canonical Form では `z:0` を省略する。

---

# 7. Absolute Time: s / e

## 7.1 概要

`s` と `e` は絶対的な有効期間を表す。

```text
s:<unix-minute>
e:<unix-minute>
```

ここで使用する値は Unix Timestamp の秒数そのものではなく、

**Unix epoch から経過した整数分**

である。

定義：

```text
unix_minute = floor(unix_time_seconds / 60)
```

---

## 7.2 UTC 基準

`s` と `e` は常に UTC ベースの Unix Minute として解釈する。

`z` は `s` または `e` の解釈に適用しない。

したがって、

```text
z:+f0,s:100,e:200
```

の場合、

```text
s/e → UTC-based Unix Minute
z    → d/w/t の local datetime にのみ適用
```

となる。

---

# 8. s の評価

`s` のみ存在する場合：

```text
s <= current_unix_minute
```

を満たすとき Active である。

例：

```text
⟦as:1,g:9q8yyk,s:100⟧
```

| current_unix_minute | 結果 |
|---:|---|
| 99 | No Match |
| 100 | Match |
| 101 | Match |

---

# 9. e の評価

`e` のみ存在する場合：

```text
current_unix_minute < e
```

を満たすとき Active である。

例：

```text
⟦as:1,g:9q8yyk,e:200⟧
```

| current_unix_minute | 結果 |
|---:|---|
| 199 | Match |
| 200 | No Match |
| 201 | No Match |

---

# 10. s と e の両方

`s` と `e` が両方存在する場合：

```text
s <= current_unix_minute < e
```

とする。

つまり、

```text
[s, e)
```

の半開区間である。

`s` と `e` が両方存在する場合、

```text
s < e
```

でなければならない。

したがって、

```text
s:100,e:200
```

は有効だが、

```text
s:200,e:100
```

は Semantic Validation Error である。

また、

```text
s:100,e:100
```

も不正である。

---

# 11. d: Month-Day Field

## 11.1 形式

```text
d:<month-day>[.<month-day>...]
```

例：

```text
d:0101
```

```text
d:0101.0505
```

`MMDD` 形式で表現する。

---

## 11.2 OR semantics

同一 `d` Field 内の複数値は OR である。

```text
d:0101.0505
```

は、

```text
January 1 OR May 5
```

を意味する。

---

## 11.3 Calendar Validation

`d` の構文上の形式は `4DIGIT` である。

ただし、実際の月日として成立するかは Semantic Validation で検証する。

例えば：

| Input | Valid | Match |
|---|---|---|
| `d:0101` | Yes | 1月1日のみ |
| `d:0231` | No | — |
| `d:1332` | No | — |
| `d:0229` | Yes | 閏年の2月29日のみ |

`d:0229` は有効な条件であるが、非閏年には Match しない。

Gregorian Calendar を使用する。

---

# 12. w: Weekday Field

## 12.1 形式

```text
w:<weekday-value>
```

曜日は次のように表現する。

```text
1 = Monday
2 = Tuesday
3 = Wednesday
4 = Thursday
5 = Friday
6 = Saturday
7 = Sunday
```

---

## 12.2 OR semantics

例えば、

```text
w:67
```

は、

```text
Saturday OR Sunday
```

を意味する。

`w` は Base36 エンコードではない。

`6` と `7` は、それぞれ曜日番号そのものを表す。

---

## 12.3 Validation

`w` の各 character は `1`〜`7` のいずれかでなければならない。

同一曜日を複数回指定してはならない。

したがって、

```text
w:67
```

は有効。

```text
w:667
```

は Semantic Validation Error である。

---

# 13. t: Time-of-Day Field

## 13.1 形式

```text
t:<start>-<end>
```

`t` は local time-of-day の1つの時間区間を表現する。

例：

```text
t:f0-uo
```

は、

```text
09:00 <= local_time < 18:00
```

を意味する。

---

# 14. local_minute_of_day

`t` の評価では、

```text
local_minute_of_day = hour * 60 + minute
```

を使用する。

範囲は、

```text
0 <= local_minute_of_day <= 1439
```

である。

例：

```text
00:00 → 0
06:00 → 360
09:00 → 540
18:00 → 1080
23:59 → 1439
```

---

# 15. t の評価

`t` は24時間周期の円環上の区間として評価する。

### start < end

```text
match =
    start <= local_minute_of_day < end
```

### start > end

```text
match =
    local_minute_of_day >= start
    OR
    local_minute_of_day < end
```

### start == end

```text
invalid
```

`start == end` は24時間を意味しない。

`t` を省略した場合にのみ、時刻条件なし、すなわち24時間を表現できる。

---

# 16. t の日跨ぎ

例えば、

```text
t:uo-a0
```

は、

```text
18:00〜24:00
OR
00:00〜06:00
```

を意味する。

これは「翌日の06:00まで」を意味するが、`d` および `w` の評価対象となる calendar date / weekday を自動的に翌日に繰り越すことはない。

各瞬間について、その瞬間の local datetime を独立して評価する。

したがって、

```text
d:0101,t:uo-a0
```

は、

```text
1月1日の local datetime で、

18:00〜24:00
OR
00:00〜06:00
```

を満たす場合に Match する。

1月2日の 00:00〜06:00 を「1月1日の夜」として扱うことはしない。

---

# 17. Local Datetime の生成

`d`、`w`、`t` の評価に使用する Local Datetime は、まず UTC 時刻に `z` を適用して生成する。

概念的には、

```text
local_datetime = utc_datetime + z
```

とする。

そこから、

```text
local_date
local_weekday
local_minute_of_day
```

を取得する。

評価対象は以下の通り。

```text
d → local_date
w → local_weekday
t → local_minute_of_day
```

重要：

```text
s / e → UTC Unix Minute
d / w / t → z 適用後の Local Datetime
```

`z` は `s` または `e` に適用してはならない。

---

# 18. Semantic Model

Parser は文字列を以下のような Semantic Model に変換する。

概念モデル：

```text
Ashiato {
    version: 1
    geohash: Geohash
    utc_offset_minutes: Integer
    start_unix_minute: Optional<Integer>
    end_unix_minute: Optional<Integer>
    dates: Optional<Set<MonthDay>>
    weekdays: Optional<Set<Weekday>>
    time_range: Optional<TimeRange>
    extensions: ExtensionMap
}
```

---

# 19. Evaluation Model

Evaluation は以下の各条件の AND として定義する。

```text
AbsoluteTimeMatch
AND
DateMatch
AND
WeekdayMatch
AND
TimeMatch
```

---

## 19.1 AbsoluteTimeMatch

`s/e` が両方ない：

```text
true
```

`s` のみ：

```text
s <= current_unix_minute
```

`e` のみ：

```text
current_unix_minute < e
```

`s/e` 両方：

```text
s <= current_unix_minute < e
```

---

## 19.2 DateMatch

`d` が存在しない場合：

```text
true
```

存在する場合：

```text
local_month_day ∈ dates
```

---

## 19.3 WeekdayMatch

`w` が存在しない場合：

```text
true
```

存在する場合：

```text
local_weekday ∈ weekdays
```

---

## 19.4 TimeMatch

`t` が存在しない場合：

```text
true
```

存在する場合は Section 15 の `t` 評価式を使用する。

---

# 20. Field の重複

v1.0 では、標準 Field を同一 Syntax 内に複数記述してはならない。

例えば、

```text
⟦as:1,g:9q8yyk,z:+f0,z:+f0⟧
```

は invalid である。

ただし、同一 Field 内の Value 重複は別問題として扱う。

例えば、

```text
d:0101.0101
```

は parse 可能であり、Canonicalization によって重複を除去する。

つまり、

```text
Field duplicate
```

と、

```text
Value duplicate
```

は別物である。

---

# 21. Extension Field

v1.0 で定義されていない Field は Extension Field として扱う。

例：

```text
x-test:foo
```

Extension Field は v1 evaluator によって意味解釈されない。

---

# 22. Extension Namespace

`x-` prefix は private extension の推奨 namespace である。

例えば、

```text
x-game:foo
x-private:bar
```

などを使用できる。

ただし、`x-` prefix は v1.0 における validity condition ではない。

したがって、

```text
foo:bar
```

のような未知 Field も v1.0 では Extension Field として受理する。

v1.0 では、将来の標準 Field と衝突しないように、独自拡張には `x-` prefix の使用を推奨する。

---

# 23. Extension と標準 Field 名

Extension Key は v1.0 の標準 Field 名と同一であってはならない。

標準 Field：

```text
as
g
z
s
e
d
w
t
```

これらは Extension Field として扱わない。

---

# 24. Extension の意味論

Extension Field は Semantic Model の一部である。

したがって、

```text
x-test:foo
```

と、

```text
x-test:bar
```

は Semantic Model として異なる。

v1 evaluator が両者の意味を解釈しないことは、両者が Semantic Model として同一であることを意味しない。

---

# 25. Unknown Extension の保持

Parser は認識した Extension Field を Semantic Model に保持する。

Canonical Serializer は保持されている Extension Field を必ず出力する。

したがって、

```text
⟦as:1,g:9q8yyk,x-test:foo⟧
```

を parse → canonical serialize した場合、`x-test:foo` が消えてはならない。

Extension Field の意味を v1 evaluator が解釈しないことと、Canonical Model から削除することは別である。

---

# 26. Extension Value

v1.0 の Extension Value は ASCII 文字による限定された形式を使用する。

```text
extension-value =
    1*(ALPHA / DIGIT / "." / "-" / "+")
```

v1.0 では URL、JSON、任意 Unicode Text などを Extension Value として直接埋め込む仕様は定義しない。

Extension Value の内部的な意味は v1 evaluator の責務ではない。

---

# 27. ABNF

以下は v1.0 の基本 Syntax Grammar である。

```abnf
ashiato =
    "⟦" "as:1" "," "g:" geohash
    *("," field)
    "⟧"

field =
      utc-offset-field
    / start-field
    / expiration-field
    / date-field
    / weekday-field
    / time-field
    / extension-field

utc-offset-field =
    "z:" signed-base36

start-field =
    "s:" base36

expiration-field =
    "e:" base36

date-field =
    "d:" month-day
    *("." month-day)

weekday-field =
    "w:" weekday-value

time-field =
    "t:" base36 "-" base36

signed-base36 =
    ["+" / "-"] base36

base36 =
    1*(DIGIT / %x61-7A)

month-day =
    4DIGIT

weekday-value =
    1*7DIGIT

geohash =
    1*geohash-char

geohash-char =
      DIGIT
    / %x62-68    ; b-h
    / %x6A-6B    ; j-k
    / %x6D-6E    ; m-n
    / %x70-7A    ; p-z

extension-field =
    extension-key ":" extension-value

extension-key =
    1*(ALPHA / DIGIT / "-")

extension-value =
    1*(ALPHA / DIGIT / "." / "-" / "+")
```

---

# 28. ABNF と Semantic Validation の責務

ABNF は Syntax の形式のみを定義する。

ABNF によって受理されることは、Semantic Validation を通過することを意味しない。

Semantic Validation では、例えば以下を検証する。

- Geohash length
- Geohash alphabet
- Geohash validity
- `z` の範囲
- `s/e` の範囲
- `s < e`
- `t` の start/end range
- `t` の start == end
- `d` の calendar validity
- `w` の曜日値
- `w` の重複
- 標準 Field の重複
- Extension Key と標準 Field 名の衝突

したがって、

```text
w:999
```

のように ABNF には一致するが意味的に不正な値は、Semantic Validation Error となる。

---

# 29. Syntax Parse と Semantic Validation

処理モデルは以下とする。

```text
Input
  ↓
Candidate Extraction
  ↓
Syntax Parse
  ↓
Semantic Validation
  ↓
Semantic Model
  ↓
Evaluation
```

Canonicalization を行う場合は、

```text
Semantic Model
  ↓
Canonical Serialization
```

とする。

---

# 30. Candidate Extraction

Ashiato Candidate は、

```text
⟦
```

から始まり、その後に現れる最初の

```text
⟧
```

までを1つの Candidate とする。

例：

```text
foo ⟦as:1,g:9q8yyk⟧ bar
```

では、

```text
⟦as:1,g:9q8yyk⟧
```

が Candidate である。

---

# 31. Nested Delimiter

Candidate が開いている間に現れる `⟦` は、新しい Candidate の開始として再帰的に扱わない。

例えば、

```text
⟦foo⟦as:1,g:9q8yyk⟧
```

では、

```text
⟦foo⟦as:1,g:9q8yyk⟧
```

全体が1つの Candidate となり、Syntax Error になる。

その後に別の `⟦` が存在する場合、Extractor は通常通り次の Candidate の探索を継続する。

---

# 32. Candidate Length Limit

Candidate の最大長は、

```text
4096 Unicode code points
```

とする。

この制限には、

```text
⟦
```

および、

```text
⟧
```

の両方を含む。

UTF-16 code unit 数ではなく Unicode code point 数で数える。

制限を超えた Candidate は invalid candidate として扱う。

---

# 33. Candidate Extraction の継続

ある Candidate が malformed であっても、その後に別の Candidate が存在する場合、Extractor は探索を継続する。

例えば、

```text
⟦invalid⟧ text ⟦as:1,g:9q8yyk⟧
```

では、

```text
Candidate 1 → invalid
Candidate 2 → valid
```

となる。

Malformed Candidate が後続 Candidate の検出を妨げてはならない。

---

# 34. Unicode Normalization

Ashiato Syntax の delimiter は literal Unicode code point として扱う。

```text
⟦
⟧
```

Parser は Candidate を Parse する前に、Unicode Normalization を行ってはならない。

同様に、Canonicalization も Unicode Normalization を行ってはならない。

Ashiato Syntax の比較・Parse・Canonicalization は、Unicode Normalization によって別文字へ変換された文字列を同一視しない。

---

# 35. Whitespace

Ashiato Syntax v1.0 の Syntax Grammar は、delimiter の直後または直前に任意の whitespace を許可するものではない。

したがって、

```text
⟦ as:1,g:9q8yyk ⟧
```

は v1.0 Syntax として valid ではない。

Ashiato Syntax は canonical representation において不要な whitespace を持たない。

---

# 36. Version

v1.0 は、

```text
as:1
```

のみをサポートする。

```text
⟦as:2,g:9q8yyk⟧
```

を v1 parser が v1 Syntax として解釈してはならない。

API 実装では、

```text
SYNTAX_ERROR
UNSUPPORTED_VERSION
```

などを区別してもよいが、エラー分類自体は本仕様では強制しない。

---

# 37. Canonicalization

Canonicalization は、

```text
Parse
→ Semantic Validation
→ Semantic Model
→ Canonical Serialization
```

によって行う。

Canonical Serializer は、同一の Semantic Model に対して常に同一の Canonical String を生成しなければならない。

---

# 38. Canonical Form

Canonical Ashiato の基本形：

```text
⟦as:1,g:<canonical-geohash>[,<canonical-field>...]⟧
```

Canonical Form では以下を保証する。

1. `as:1` は必ず存在する
2. `g` は必ず存在する
3. `z:0` は省略する
4. Base36 は lowercase にする
5. `z` の正数には `+` を付ける
6. `z` の負数には `-` を付ける
7. `s/e/t` は unsigned Base36 とする
8. 不要な leading zero を削除する
9. `d` の Value は昇順にする
10. `w` の Value は昇順にする
11. `d/w` の Value 重複を除去する
12. Standard Field は固定順序で出力する
13. Extension Field は保持する
14. Extension Field は決定的な順序で出力する
15. Unicode Normalization は行わない
16. 不要な whitespace は出力しない

---

# 39. Canonical Numeric Representation

## 39.1 z

`z` は signed Base36。

```text
+540 → +f0
-300 → -8c
0    → z field omitted
+0   → z field omitted
-0   → z field omitted
```

---

## 39.2 s / e / t

`s`、`e`、`t` は unsigned Base36 である。

符号は使用しない。

例えば、

```text
100 decimal → 2s
200 decimal → 5k
540 decimal → f0
1080 decimal → uo
```

したがって、

```text
s:100
```

の Canonical Form は、

```text
s:2s
```

である。

---

# 40. Canonical Field Order

Standard Field の Canonical Order は以下とする。

```text
z
s
e
d
w
t
```

したがって、

```text
⟦as:1,g:9q8yyk,t:f0-uo,z:+f0,d:0101,s:2s⟧
```

は Canonical Form では、

```text
⟦as:1,g:9q8yyk,z:+f0,s:2s,d:0101,t:f0-uo⟧
```

となる。

---

# 41. Canonical d

`d` の Value は、

1. 重複を除去
2. 数値的な MMDD 順に並べる

とする。

例えば、

```text
d:0505.0101.0505
```

は、

```text
d:0101.0505
```

となる。

---

# 42. Canonical w

`w` の Value は、

1. 重複を除去
2. 数値昇順に並べる

とする。

例えば、

```text
w:765
```

は、

```text
w:567
```

となる。

---

# 43. Canonical Extension

Extension Field は Semantic Model に保持され、Canonical Form に必ず出力する。

Extension Key は決定的な順序で並べる。

v1.0 では ASCII lexicographic order を使用する。

Extension Value は、v1.0 が意味を解釈しないため、意味論的な変換を行わない。

したがって、

```text
x-test:FOO
```

を、

```text
x-test:foo
```

へ変換してはならない。

Extension Value の大小文字は区別される。

---

# 44. Semantic Equality

2つの Ashiato が Semantic Equality で同一であるとは、Canonical Serialization の結果が同一であることとする。

したがって、

```text
Canonical(A) == Canonical(B)
```

なら、

```text
A == B
```

である。

Extension Field も Semantic Model の一部であるため、Semantic Equality に参加する。

例えば、

```text
⟦as:1,g:9q8yyk,x-test:foo⟧
```

と、

```text
⟦as:1,g:9q8yyk,x-test:bar⟧
```

は Semantic Equality では異なる。

---

# 45. Behavioral Equality

v1 evaluator が解釈する標準 Field のみを比較した場合、異なる Extension を持つ2つの Ashiato が同じ Active 判定結果になることがある。

これは Semantic Equality とは別である。

例えば、

```text
A = ⟦as:1,g:9q8yyk,x-test:foo⟧
B = ⟦as:1,g:9q8yyk,x-test:bar⟧
```

は、

```text
Semantic Equality → 不一致
```

である。

一方、v1 evaluator が Extension を無視する限り、

```text
Behavioral result → 同一
```

となる場合がある。

v1.0 では Behavioral Equality を独立した API として定義することは要求しない。

---

# 46. Determinism

v1.0 の Parser、Semantic Validator、Evaluator、および Canonical Serializer は決定的でなければならない。

同一の入力と同一の評価時刻に対して、同一の結果を返す。

Canonical Serializer は、同一の Semantic Model に対して常に同一の Canonical String を生成する。

特に、

```text
Canonical(Canonical(x)) == Canonical(x)
```

を満たさなければならない。

また、

```text
Parse(Canonical(x))
```

は、元の `x` と同一の Semantic Model を生成しなければならない。

---

# 47. Privacy Considerations

Ashiato Syntax は位置および時間条件を公開文字列として表現する。

したがって、利用者が高精度の Geohash と時間条件を組み合わせた場合、位置情報だけでなく時間的パターンも第三者に推測される可能性がある。

例えば、

```text
⟦as:1,g:<high-precision-geohash>,z:+f0,d:0101,t:uo-a0⟧
```

は、

- 特定の場所
- UTC+09:00
- 毎年1月1日
- 18:00〜翌06:00相当の local time 条件

を公開する。

さらに `s` / `e` と組み合わせることで、期間限定のイベント等を推測できる場合がある。

Ashiato Syntax は、このような Location Privacy および Temporal Privacy を自動的に保護する機能を提供しない。

位置・時間情報は、設計上公開情報となり得る。

---

# 48. Server Communication

Ashiato Syntax は、現在位置をサーバーへ送信することを要求しない。

ただし、本仕様はサーバーへの現在位置送信を禁止するものでもない。

現在位置をどこで取得し、どこで比較し、サーバーへ何を送信するかは Client / Application の責務である。

---

# 49. Non-Goals

v1.0 では以下を仕様化しない。

- 距離計算
- 発見半径
- GPS Accuracy
- Geolocation Permission
- Ownership
- Claim
- Score
- Cooldown
- Anti-Cheat
- Game Mechanics
- Server API
- Database Schema
- SNS API
- IANA Time Zone
- DST Rule
- 複数 Time Range
- 任意 Boolean Expression
- URL / JSON / Markdown 等の Extension Encoding
- SNS 固有の編集・引用・Reply・Repost 機能

---

# 50. v1.0 における t の制限

v1.0 の `t` は1つの時間区間のみを表現する。

例えば、

```text
09:00〜12:00
OR
18:00〜21:00
```

を1つの `t` Field に直接記述する Syntax は存在しない。

これは意図的な制限である。

複数時間帯が必要な場合は、将来の仕様拡張で別途定義する。

---

# 51. Test Vectors

以下は v1.0 Reference Test Vector の例である。

## 51.1 Basic

```text
⟦as:1,g:9q8yyk⟧
```

Valid.

---

## 51.2 Fixed UTC Offset

```text
⟦as:1,g:9q8yyk,z:+f0⟧
```

Valid.

意味：

```text
UTC+09:00
```

---

## 51.3 Zero Offset

```text
⟦as:1,g:9q8yyk,z:0⟧
```

Valid.

Canonical Form：

```text
⟦as:1,g:9q8yyk⟧
```

---

## 51.4 Negative Offset

```text
⟦as:1,g:9q8yyk,z:-8c⟧
```

Valid.

意味：

```text
-300 minutes
= UTC-05:00
```

---

## 51.5 Absolute Start

```text
⟦as:1,g:9q8yyk,s:2s⟧
```

`current_unix_minute = 100`

→ Match

`current_unix_minute = 99`

→ No Match

---

## 51.6 Absolute End

```text
⟦as:1,g:9q8yyk,e:5k⟧
```

`current_unix_minute = 199`

→ Match

`current_unix_minute = 200`

→ No Match

---

## 51.7 Absolute Interval

```text
⟦as:1,g:9q8yyk,s:2s,e:5k⟧
```

意味：

```text
100 <= current_unix_minute < 200
```

---

## 51.8 Invalid Absolute Interval

```text
⟦as:1,g:9q8yyk,s:5k,e:2s⟧
```

Semantic Validation Error.

---

## 51.9 Normal Time Range

```text
⟦as:1,g:9q8yyk,t:f0-uo⟧
```

意味：

```text
09:00 <= local_time < 18:00
```

境界：

```text
local_minute_of_day = 540
→ Match

local_minute_of_day = 1079
→ Match

local_minute_of_day = 1080
→ No Match
```

---

## 51.10 Cross-Midnight Time Range

```text
⟦as:1,g:9q8yyk,t:uo-a0⟧
```

意味：

```text
18:00〜24:00
OR
00:00〜06:00
```

境界：

```text
1079 → No Match
1080 → Match
1439 → Match
0    → Match
359  → Match
360  → No Match
```

---

## 51.11 Invalid Zero-Length Time

```text
⟦as:1,g:9q8yyk,t:0-0⟧
```

Semantic Validation Error.

---

## 51.12 Month-Day

```text
⟦as:1,g:9q8yyk,d:0101.0505⟧
```

意味：

```text
January 1 OR May 5
```

---

## 51.13 Weekday

```text
⟦as:1,g:9q8yyk,w:67⟧
```

意味：

```text
Saturday OR Sunday
```

---

## 51.14 Combined Recurring Conditions

```text
⟦as:1,g:9q8yyk,z:+f0,d:0101,w:67,t:uo-a0⟧
```

意味：

```text
local date = January 1
AND
local weekday = Saturday OR Sunday
AND
local time = 18:00〜06:00
```

---

## 51.15 d + w

```text
⟦as:1,g:9q8yyk,d:0101.0505,w:67⟧
```

意味：

```text
(January 1 OR May 5)
AND
(Saturday OR Sunday)
```

---

## 51.16 Leap Day

```text
⟦as:1,g:9q8yyk,d:0229⟧
```

Valid.

閏年：

→ Match

非閏年：

→ No Match

---

## 51.17 Invalid Calendar Date

```text
⟦as:1,g:9q8yyk,d:0231⟧
```

Semantic Validation Error.

---

## 51.18 Extension

```text
⟦as:1,g:9q8yyk,x-test:foo⟧
```

Valid.

v1 evaluator は `x-test` の意味を解釈しない。

Canonical Serialization では `x-test:foo` を保持する。

---

## 51.19 Extension Semantic Difference

```text
⟦as:1,g:9q8yyk,x-test:foo⟧
```

と、

```text
⟦as:1,g:9q8yyk,x-test:bar⟧
```

は Semantic Equality では異なる。

---

## 51.20 Canonical z

Input：

```text
⟦as:1,g:9q8yyk,z:+000f0⟧
```

Canonical：

```text
⟦as:1,g:9q8yyk,z:+f0⟧
```

---

## 51.21 Canonical Zero z

Input：

```text
⟦as:1,g:9q8yyk,z:-0⟧
```

Canonical：

```text
⟦as:1,g:9q8yyk⟧
```

---

## 51.22 Canonical s/e

Input：

```text
⟦as:1,g:9q8yyk,s:0002s,e:0005k⟧
```

Canonical：

```text
⟦as:1,g:9q8yyk,s:2s,e:5k⟧
```

---

## 51.23 Canonical d

Input：

```text
⟦as:1,g:9q8yyk,d:0505.0101.0505⟧
```

Canonical：

```text
⟦as:1,g:9q8yyk,d:0101.0505⟧
```

---

## 51.24 Canonical w

Input：

```text
⟦as:1,g:9q8yyk,w:765⟧
```

Canonical：

```text
⟦as:1,g:9q8yyk,w:567⟧
```

---

## 51.25 Field Ordering

Input：

```text
⟦as:1,g:9q8yyk,t:f0-uo,d:0101,s:2s,z:+f0⟧
```

Canonical：

```text
⟦as:1,g:9q8yyk,z:+f0,s:2s,d:0101,t:f0-uo⟧
```

---

## 51.26 z Does Not Affect s/e

```text
⟦as:1,g:9q8yyk,z:+f0,s:100,e:200⟧
```

`s/e` は UTC-based Unix Minute として評価する。

`z:+f0` は `s/e` に適用しない。

---

## 51.27 t Boundary

```text
⟦as:1,g:9q8yyk,t:f0-uo⟧
```

```text
540  → Match
1079 → Match
1080 → No Match
```

---

## 51.28 Cross-Midnight Boundary

```text
⟦as:1,g:9q8yyk,t:uo-a0⟧
```

```text
1079 → No Match
1080 → Match
1439 → Match
0    → Match
359  → Match
360  → No Match
```

---

# 52. Reference Evaluation Algorithm

概念的な Evaluation は以下のように実装できる。

```text
evaluate(ashiato, current_utc_datetime):

    current_unix_minute =
        floor(current_unix_time_seconds / 60)

    if s exists and current_unix_minute < s:
        return false

    if e exists and current_unix_minute >= e:
        return false

    local_datetime =
        current_utc_datetime + z

    if d exists:
        if local_month_day not in d:
            return false

    if w exists:
        if local_weekday not in w:
            return false

    if t exists:
        start = t.start
        end   = t.end
        minute = local_minute_of_day

        if start == end:
            invalid

        if start < end:
            if not (start <= minute < end):
                return false

        if start > end:
            if not (minute >= start or minute < end):
                return false

    return true
```

Extension Field は v1 evaluator では無視する。

---

# 53. Reference Canonicalization Algorithm

概念的には以下の手順で Canonicalization を行う。

```text
parse(input)

→ semantic validation

→ construct semantic model

→ normalize semantic model

    - z = 0 → omit
    - remove duplicate d values
    - sort d values
    - sort w values
    - normalize Base36
    - remove leading zeros
    - preserve extensions
    - sort fields deterministically

→ serialize

→ canonical string
```

---

# 54. Canonicalization の必須性質

Canonical Serializer は以下を満たさなければならない。

### Idempotence

```text
Canonical(Canonical(x))
=
Canonical(x)
```

### Semantic Preservation

```text
Parse(x)
```

と、

```text
Parse(Canonical(x))
```

は同一の Semantic Model を生成する。

### Determinism

同一の Semantic Model に対して、

```text
Serialize(model)
```

は常に同じ文字列を返す。

---

# 55. 実装者向け重要事項

Ashiato v1.0 の実装では、以下を明確に分離することを推奨する。

```text
Extractor
    ↓
Parser
    ↓
Semantic Validator
    ↓
Semantic Model
    ↓
Evaluator
    ↓
Canonical Serializer
```

特に、

```text
Syntax
```

と、

```text
Semantic Validation
```

を混同してはならない。

また、

```text
UTC Unix Minute
```

と、

```text
Local Date / Weekday / Time
```

も別の概念として扱う。

---

# 56. 重要な設計原則

Ashiato v1.0 の中心的な設計原則は以下である。

### 1. Field 間は AND

```text
d:0101,w:67
```

↓

```text
d AND w
```

### 2. Field 内 Value は OR

```text
d:0101.0505
```

↓

```text
0101 OR 0505
```

### 3. z は Local Time のためだけに使用する

```text
z → d/w/t
```

### 4. s/e は UTC Unix Minute

```text
s/e → UTC
```

### 5. t の日跨ぎは d/w の日付を繰り越さない

```text
t:uo-a0
```

は単純な local time-of-day の円環区間である。

### 6. g は Geohash Cell

`g` は距離判定そのものではない。

### 7. Extension は保持する

v1 evaluator は解釈しなくても、Canonical Model から削除しない。

### 8. Canonical Form は決定的

同じ Semantic Model は常に同じ Canonical String を持つ。

---

# 57. Summary

Ashiato Syntax v1.0 は、

```text
⟦as:1,g:<geohash>[,<field>...]⟧
```

という非常に小さな形式で、

```text
Location
+
Absolute Time
+
Recurring Local Time
```

を表現する。

時間条件は、

```text
s/e → UTC Unix Minute
z    → Local Datetime
d/w/t → Local Date / Weekday / Time
```

という明確なモデルで評価する。

論理構造は、

```text
fields = AND
values = OR
```

に限定する。

Ashiato Syntax 自体は、

```text
location matching
distance
GPS
game mechanics
server behavior
SNS behavior
```

を規定しない。

この責務分離によって、Ashiato Syntax は特定の SNS やゲームに依存しない、軽量な位置・時間条件の Micro-Syntax として利用できる。
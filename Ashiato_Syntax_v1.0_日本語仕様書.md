# Ashiato Syntax v1.0 仕様書

**Status:** Proposed / v1.0\
**言語:** 日本語\
**対象:** Ashiato Syntax
を実装するパーサー、バリデータ、Canonicalizer、クライアント実装

------------------------------------------------------------------------

## 1. 概要

Ashiato Syntax
は、既存のSNSや投稿サービスの本文に埋め込める、小さな位置・時間記述用のマイクロシンタックスである。

Ashiato Syntax
は、**「どこで」「いつ有効か」**を記述するためのものであり、発見距離、ゲームルール、GPS精度、取得方法、サーバー上の位置情報処理などを規定しない。

基本形は次の通り。

``` text
⟦as:1,g:9q8yyk⟧
```

時間・曜日などの条件を追加できる。

``` text
⟦as:1,g:9q8yyk,z:+f0,w:67,t:uo-a0⟧
```

この例は、固定UTCオフセット UTC+09:00
において、土曜日または日曜日の18:00〜翌06:00に該当するローカル時刻を条件として表す。

------------------------------------------------------------------------

## 2. 設計原則

Ashiato Syntax v1.0 は、以下を基本原則とする。

1.  **Syntax は位置と時間条件のみを表現する。**
2.  **発見距離やゲーム性はクライアントに委ねる。**
3.  **位置情報の表現には既存の Geohash を使用する。**
4.  **タイムゾーンは IANA Time Zone ではなく固定 UTC Offset とする。**
5.  **絶対時間条件と周期時間条件を分離する。**
6.  **フィールド間は AND、同一フィールド内の複数値は OR とする。**
7.  **ABNF は構文を定義し、意味的制約は Semantic Validation
    で定義する。**
8.  **Canonical Form は Semantic Model
    から一意に生成できるものとする。**
9.  **未知の拡張フィールドは、v1定義フィールドの意味に影響を与えてはならない。**
10. **Ashiato Syntax はSNSの特定機能に依存しない。**

------------------------------------------------------------------------

# 3. Syntax

## 3.1 基本構造

Ashiato Syntax は次の構造を持つ。

``` text
⟦as:1,g:<geohash>[,<field>...]⟧
```

`as:1` と `g:<geohash>` は固定ヘッダーであり、必須である。

-   `as:1` --- Ashiato Syntax のメジャーバージョン
-   `g:` --- Geohash
-   その他のフィールド --- オプション

フィールドの順序は v1.0 では Canonical Form により規定する。

------------------------------------------------------------------------

## 3.2 区切り文字

開始 delimiter は次の文字である。

``` text
⟦
```

終了 delimiter は次の文字である。

``` text
⟧
```

これらは ASCII の代替文字ではない。

以下は Ashiato Syntax の delimiter ではない。

``` text
<<
>>
［
］
```

パーサーは、候補文字列を解析する前に Unicode 正規化を行ってはならない。

------------------------------------------------------------------------

# 4. フィールド

v1.0 で定義するフィールドは以下の通り。

  Field          必須 意味
  ------------ ------ ----------------------
  `as`            Yes Syntax version
  `g`             Yes Geohash
  `z`              No 固定 UTC Offset
  `s`              No 開始 Unix minute
  `e`              No 終了 Unix minute
  `d`              No 月日条件
  `w`              No 曜日条件
  `t`              No ローカル時刻条件
  拡張 field       No 将来・実装固有の拡張

同一フィールドを v1.0 の1つの Ashiato 内に複数回記述してはならない。

例：

``` text
⟦as:1,g:9q8yyk,w:67,w:1⟧
```

は invalid である。

同一フィールドに複数値が必要な場合は、そのフィールド内で値を列挙する。

``` text
w:167
```

------------------------------------------------------------------------

# 5. Version

## 5.1 `as`

``` text
as:1
```

は Ashiato Syntax v1 を意味する。

v1.0 parser は `as:1` 以外のメジャーバージョンを v1 Syntax
として解釈してはならない。

`as:1` は固定ヘッダーの一部であり、Canonical Form でも必ず出力する。

------------------------------------------------------------------------

# 6. Location

## 6.1 `g`

`g` は標準的な Geohash を表す。

例：

``` text
g:9q8yyk
```

Ashiato Syntax は独自の緯度・経度エンコード方式を定義しない。

`g` の意味は既存の Geohash 仕様に従う。

v1.0 では Geohash の文字集合として次を使用する。

``` text
0123456789bcdefghjkmnpqrstuvwxyz
```

大文字は使用しない。

### 6.1.1 Geohash length

v1.0 では Geohash length は **1〜12文字**とする。

-   1文字以上であること
-   12文字を超える場合は invalid
-   Canonical Form では小文字を使用する

### 6.1.2 Geohash はセルを表す

`g` は一点の座標ではなく、Geohash に対応する**空間セル**を表す。

したがって、Ashiato Syntax 自体は以下を規定しない。

-   セル内に現在位置が入っていれば発見とするか
-   セル中心からの距離を使うか
-   現在位置とセルとの距離を使うか
-   発見半径を何mにするか
-   GPS精度をどう考慮するか

これらはクライアント側の責務である。

------------------------------------------------------------------------

# 7. Fixed UTC Offset

## 7.1 `z`

`z` は **固定 UTC Offset** を表す。

これはタイムゾーン名ではない。

``` text
z:+f0
```

は UTC+09:00 を意味する。

``` text
Asia/Tokyo
```

のような IANA Time Zone ID は使用しない。

### 7.1.1 Base36

`z` の数値は符号付き Base36 整数として表現する。

Base36 のアルファベットは小文字を使用する。

``` text
0-9
a-z
```

例：

``` text
+f0 = +540
-8c = -300
```

したがって、

``` text
z:+f0
```

は UTC+09:00、

``` text
z:-8c
```

は UTC-05:00 を意味する。

### 7.1.2 符号

正数は `+` を付ける。

``` text
+f0
```

負数は `-` を付ける。

``` text
-8c
```

0 は符号を付けない。

``` text
0
```

入力として `+0` または `-0` が構文上存在しても、Semantic Model 上の値は
0 とする。

Canonical Form では `z` を省略する。

### 7.1.3 Offset の範囲

v1.0 の `z` は分単位の UTC Offset とし、値は次の範囲とする。

``` text
-1440 <= z <= +1440
```

実際の地域で一般的でない Offset であっても、固定 Offset
としてこの範囲内なら表現可能である。

v1.0 は DST や歴史的タイムゾーン規則を解釈しない。

------------------------------------------------------------------------

# 8. Absolute Time

## 8.1 `s`

`s` は開始 Unix minute を表す。

Unix time を秒で取得した後、

``` text
unix_minute = floor(unix_time_seconds / 60)
```

として得られる整数である。

`s` は Unix timestamp そのものではない。

------------------------------------------------------------------------

## 8.2 `e`

`e` は終了 Unix minute を表す。

同様に、

``` text
unix_minute = floor(unix_time_seconds / 60)
```

として表現する。

------------------------------------------------------------------------

## 8.3 Unix minute の範囲

v1.0 では `s` と `e` の値は、

``` text
0 <= value <= 2^63 - 1
```

の範囲とする。

負の Unix minute は v1.0 では使用しない。

------------------------------------------------------------------------

## 8.4 `s` と `e` の関係

`s` と `e` が両方存在する場合、

``` text
s < e
```

でなければならない。

したがって、`s == e` および `s > e` は invalid である。

------------------------------------------------------------------------

## 8.5 区間の境界

`s` / `e` は半開区間として評価する。

``` text
s <= current_minute < e
```

したがって、

``` text
s:100,e:200
```

は、

``` text
100以上 かつ 200未満
```

を意味する。

この設計により、

``` text
s:100,e:200
```

と

``` text
s:200,e:300
```

を隙間なく隣接させることができる。

------------------------------------------------------------------------

# 9. Local Date / Weekday / Time

`d`、`w`、`t` はローカル日時に対して評価する。

評価対象の UTC 時刻に `z` の固定 UTC Offset を適用し、

``` text
local_datetime = utc_datetime + offset
```

を求める。

その後、

``` text
local_date
local_weekday
local_time
```

を取得する。

意味は以下の通り。

``` text
d → local_date
w → local_weekday
t → local_time
```

つまり、`d`、`w`、`t` はすべて**評価対象となる瞬間の local datetime**
を基準に評価する。

------------------------------------------------------------------------

# 10. Date Condition

## 10.1 `d`

`d` は月日条件を表す。

例：

``` text
d:0101
```

は1月1日を意味する。

複数値を `.` で区切る。

``` text
d:0101.0505.1225
```

は、

``` text
1月1日 OR 5月5日 OR 12月25日
```

を意味する。

------------------------------------------------------------------------

## 10.2 月日の形式

月日は常に4桁で表す。

``` text
MMDD
```

例：

``` text
0101
0505
1225
```

------------------------------------------------------------------------

## 10.3 カレンダー検証

ABNF は `MMDD` の文字形式のみを規定する。

カレンダー上存在しない月日は Semantic Validation で扱う。

例：

``` text
d:1332
```

は invalid。

一方、

``` text
d:0229
```

は有効な Syntax である。

`0229` は、評価対象の年が閏年の場合にのみ match する。

v1.0 は **proleptic Gregorian calendar** を使用する。

------------------------------------------------------------------------

# 11. Weekday Condition

## 11.1 `w`

`w` は曜日集合を表す。

曜日は以下の数字で表す。

     値 曜日
  ----- --------
    `1` 月曜日
    `2` 火曜日
    `3` 水曜日
    `4` 木曜日
    `5` 金曜日
    `6` 土曜日
    `7` 日曜日

例：

``` text
w:67
```

は、

``` text
土曜日 OR 日曜日
```

を意味する。

------------------------------------------------------------------------

## 11.2 `w` は Base36 ではない

`w` の数字は Base36 数値ではない。

例えば、

``` text
w:67
```

の `6` と `7` は、それぞれ曜日番号そのものを表す。

`w` は v1.0 において、Base36 ではない唯一の numeric-looking field
である。

------------------------------------------------------------------------

## 11.3 重複

同じ曜日番号を複数回記述してはならない。

``` text
w:667
```

は invalid。

Canonical Form では曜日番号を昇順にする。

例：

``` text
w:751
```

は Semantic Model 上、

``` text
{1,5,7}
```

となり、Canonical Form では、

``` text
w:157
```

となる。

------------------------------------------------------------------------

# 12. Time-of-Day Condition

## 12.1 `t`

`t` はローカル時刻の範囲を表す。

値は Base36 で分単位の時刻を表す。

1日の範囲は、

``` text
0 <= minute <= 1439
```

である。

時刻は、

``` text
minute = hour * 60 + minute
```

として解釈する。

例：

``` text
540 = 09:00
1080 = 18:00
```

Base36 表現では、

``` text
540  = f0
1080 = uo
```

となる。

------------------------------------------------------------------------

## 12.2 半開区間

`t` は半開区間として評価する。

通常区間では、

``` text
start < end
```

の場合、

``` text
start <= local_minute < end
```

である。

------------------------------------------------------------------------

## 12.3 日跨ぎ

`start > end` の場合、範囲は日跨ぎとする。

評価式は、

``` text
local_minute >= start OR local_minute < end
```

である。

例：

``` text
t:uo-a0
```

は、

``` text
18:00 <= local_time OR local_time < 06:00
```

を意味する。

したがって、

``` text
18:00〜翌06:00
```

に相当する。

------------------------------------------------------------------------

## 12.4 `start == end`

``` text
t:0-0
```

のように `start == end` となる `t` は invalid。

`t` における `start == end` は24時間を意味しない。

24時間有効を表す場合は `t` を省略する。

------------------------------------------------------------------------

## 12.5 `0-1439` は24時間ではない

`t:0-13z` は、

``` text
00:00 <= local_time < 23:59
```

である。

これは24時間ではない。

24時間有効を表す場合は `t` を省略する。

------------------------------------------------------------------------

# 13. 日跨ぎと `d` / `w` の関係

これは v1.0 の重要な規則である。

`t` が日跨ぎしても、`d` や `w`
の評価基準となる日付を固定したり翌日に繰り越したりしない。

すべての条件は、**評価対象となる瞬間の local datetime**
に対して独立に評価する。

例えば、

``` text
w:1,t:uo-a0
```

は、

``` text
月曜日 18:00〜23:59...
```

と、

``` text
火曜日 00:00〜06:00...
```

の両方を意味するわけではない。

火曜日の 00:00〜06:00 は `w:1` を満たさないため、match しない。

つまり、

``` text
w:1,t:uo-a0
```

は「月曜夜〜火曜朝」という営業時間型の意味ではなく、

**評価対象の local datetime が月曜日であり、その local time が
18:00〜24:00 または 00:00〜06:00 の範囲にある**

という意味である。

------------------------------------------------------------------------

# 14. 条件論理

Ashiato Syntax の論理構造は非常に単純である。

``` text
Active = AND(fields)
Field  = OR(values)
```

つまり、

-   異なるフィールド間 → AND
-   同じフィールド内の複数値 → OR

となる。

例えば、

``` text
⟦as:1,g:9q8yyk,d:0101.0505,w:67,t:uo-a0⟧
```

は、

``` text
(1月1日 OR 5月5日)
AND
(土曜日 OR 日曜日)
AND
(18:00〜24:00 OR 00:00〜06:00)
```

である。

複雑な任意論理式、NOT、括弧、OR グループなどは v1.0 ではサポートしない。

------------------------------------------------------------------------

# 15. Default

`z` が省略された場合、

``` text
z:0
```

と意味的に同値である。

例えば、

``` text
⟦as:1,g:9q8yyk⟧
```

と、

``` text
⟦as:1,g:9q8yyk,z:0⟧
```

は Semantic Model 上同一である。

ただし Canonical Form では、値が0の `z` は省略する。

したがって両方とも、

``` text
⟦as:1,g:9q8yyk⟧
```

に Canonicalize される。

------------------------------------------------------------------------

# 16. Extension Fields

v1.0 では将来の拡張のため、未知フィールドを許容する。

例：

``` text
x-example:foo
```

## 16.1 Extension の基本原則

未知フィールドは、

-   v1定義フィールドの意味を変更してはならない
-   v1 evaluator はその意味を解釈しない
-   parser は可能な限り保持する
-   serializer は保持した未知フィールドを再出力してよい

とする。

推奨される private extension の命名規則として、

``` text
x-...
```

を使用する。

`x-`
を持たない未知フィールドは、将来の標準仕様で予約される可能性がある。

------------------------------------------------------------------------

## 16.2 Extension field の大文字・小文字

Extension key は **case-sensitive** とする。

ただし v1.0 の推奨命名規則では、extension key は小文字のみを使用する。

例えば、

``` text
x-test
X-test
```

は異なる key である。

------------------------------------------------------------------------

## 16.3 Extension value

v1.0 の extension value は次の ASCII 文字のみを許可する。

``` text
ALPHA
DIGIT
.
-
+
```

空の extension value は許可しない。

したがって、

``` text
x-test:foo
x-test:123
x-test:a-b
```

は有効。

``` text
x-test:
```

は invalid。

URL、JSON、任意のUnicode文字列などを extension value
に直接格納することは v1.0 では規定しない。

------------------------------------------------------------------------

# 17. ABNF

以下は v1.0 の構文を表す ABNF である。

``` abnf
ashiato = "⟦" "as:1" "," "g:" geohash *("," field) "⟧"

field =
      utc-offset-field
    / start-field
    / expiration-field
    / date-field
    / weekday-field
    / time-field
    / extension-field

utc-offset-field = "z:" signed-base36
start-field      = "s:" base36
expiration-field = "e:" base36
date-field       = "d:" month-day *("." month-day)
weekday-field    = "w:" weekday-value
time-field       = "t:" base36 "-" base36

signed-base36 = ["+" / "-"] base36
base36        = 1*(DIGIT / %x61-7A)

month-day     = 4DIGIT
weekday-value = 1*7DIGIT

geohash =
    1*(%x30-39 / %x62-68 / %x6A-6B /
       %x6D-6E / %x70-7A)

extension-field = extension-key ":" extension-value
extension-key   = 1*(ALPHA / DIGIT / "-")
extension-value = 1*(ALPHA / DIGIT / "." / "-" / "+")
```

## 17.1 ABNF の責務

ABNF は**構文のみ**を定義する。

ABNF で受理されたことは、Semantic Validation
に成功したことを意味しない。

以下は Semantic Validation の責務である。

-   数値範囲
-   Geohash length
-   Geohash alphabet
-   UTC Offset の範囲
-   フィールドの重複
-   `s < e`
-   `t` の start/end の関係
-   月日の妥当性
-   曜日の妥当性
-   extension の制約
-   その他の意味論的制約

------------------------------------------------------------------------

# 18. Semantic Validation

Parser は Syntax Parse と Semantic Validation を分離する。

推奨処理順序：

``` text
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
Canonical Serialization
```

以下は invalid である。

### 18.1 必須 field の欠落

``` text
⟦as:1⟧
```

### 18.2 `g` の空値

``` text
⟦as:1,g:⟧
```

### 18.3 不正な Geohash

``` text
⟦as:1,g:9q8yyi⟧
```

### 18.4 Geohash length 超過

12文字を超える Geohash。

### 18.5 field 重複

``` text
⟦as:1,g:9q8yyk,z:0,z:+f0⟧
```

### 18.6 不正な weekday

``` text
w:0
w:8
w:999
```

### 18.7 重複 weekday

``` text
w:667
```

### 18.8 不正な date

``` text
d:1332
d:0000
```

### 18.9 `t` の同値

``` text
t:0-0
```

### 18.10 `s >= e`

``` text
s:200,e:100
s:100,e:100
```

------------------------------------------------------------------------

# 19. Canonicalization

## 19.1 基本方針

Canonicalization は、

``` text
parse
→ validate
→ semantic model
→ canonical serialize
```

として定義する。

同じ Semantic Model は、必ず同じ Canonical String に変換される。

したがって、

``` text
Canonical(A) == Canonical(B)
```

なら、A と B は v1.0 の Semantic Model 上同一である。

------------------------------------------------------------------------

## 19.2 Canonical field order

Canonical Form の field order は次の通り。

``` text
as
g
z
s
e
d
w
t
extension fields
```

`as` と `g` は必ず先頭。

------------------------------------------------------------------------

## 19.3 Default の省略

`z` の値が0の場合、Canonical Formでは `z` を省略する。

``` text
z:0
z:+0
z:-0
```

はいずれも Canonical Form では省略される。

------------------------------------------------------------------------

## 19.4 数値

Base36 の数値は、

-   小文字
-   不要な先頭ゼロを削除
-   正数は `+`
-   負数は `-`
-   0 は符号なし

とする。

例：

``` text
+000f0 → +f0
-0008c → -8c
000    → 0
```

ただし `z:0` は Default Field のため省略される。

------------------------------------------------------------------------

## 19.5 Date

`d` の値は月日順に昇順で並べる。

``` text
d:0505.0101
```

は、

``` text
d:0101.0505
```

になる。

重複値は Semantic Model で除去する。

------------------------------------------------------------------------

## 19.6 Weekday

`w` は昇順に並べる。

``` text
w:751
```

は、

``` text
w:157
```

になる。

------------------------------------------------------------------------

## 19.7 Extension field

Extension field は key の ASCII lexicographical order で並べる。

同一 key の重複は v1.0 では許可されない。

Extension value は v1.0 の Semantic Model では意味的な正規化を行わない。

つまり、extension value
の内容を勝手に小文字化したり、URL正規化したりしてはならない。

------------------------------------------------------------------------

# 20. Candidate Extraction

Ashiato Syntax は本文中の文字列として存在することを想定する。

例：

``` text
今日はここに行った ⟦as:1,g:9q8yyk⟧ また行きたい。
```

Extractor は、

``` text
⟦
```

を candidate の開始として認識し、その後に現れる最初の、

``` text
⟧
```

を candidate の終了として扱う。

v1.0 は nested delimiter をサポートしない。

例えば、

``` text
⟦foo⟦as:1,g:9q8yyk⟧bar⟧
```

では、最初の `⟧` までが1つの candidate である。

その candidate が invalid であっても、後続テキスト中に別の `⟦`
が存在する場合は、extractor はその後続 candidate の探索を継続する。

------------------------------------------------------------------------

## 20.1 最大 candidate length

実装者間の DoS 耐性とSNS本文処理の予測可能性を確保するため、v1.0 parser
は candidate length を **4096 Unicode code points 以下**とする。

4096 を超える candidate は invalid candidate として扱う。

これは Ashiato の意味論ではなく、parser resource limit である。

------------------------------------------------------------------------

# 21. 空白

Ashiato Syntax の内部に ASCII whitespace を挿入してはならない。

例えば、

``` text
⟦ as:1,g:9q8yyk ⟧
```

は invalid。

``` text
⟦as:1,g:9q8yyk⟧
```

は valid。

Ashiato の前後の本文に空白が存在することは問題ない。

``` text
foo ⟦as:1,g:9q8yyk⟧ bar
```

は valid。

------------------------------------------------------------------------

# 22. Unicode Normalization

Ashiato candidate は、parse 前に Unicode Normalization
を適用してはならない。

特に、

-   NFC
-   NFD
-   NFKC
-   NFKD

などによって delimiter や文字列を変換してから parse してはならない。

Ashiato Syntax の delimiter は literal Unicode code point として扱う。

SNSやIMEによる外部の文字変換については、Ashiato Syntax の責務外である。

------------------------------------------------------------------------

# 23. 複数の Ashiato

同一投稿内に複数の valid Ashiato が存在することを禁止しない。

例：

``` text
大阪 ⟦as:1,g:9q8yyk⟧
東京 ⟦as:1,g:xn76ur⟧
```

それぞれ独立した Ashiato candidate として扱う。

v1.0 Syntax は、

-   どちらを優先するか
-   どちらをゲーム対象にするか
-   複数 Ashiato を統合するか
-   重複 Ashiato をどう表示するか

を規定しない。

これらはクライアント・アプリケーションの責務である。

------------------------------------------------------------------------

# 24. Location / Temporal Privacy

Ashiato Syntax
は、位置と時間条件を**公開可能な文字列として記述する設計**である。

したがって、

``` text
g
z
d
w
t
s
e
```

の組み合わせによって、位置・曜日・時刻・期間などの情報が第三者に推測可能になる場合がある。

特に高精度の Geohash
と具体的な時間条件を組み合わせる場合、意図せず詳細な行動情報を公開する可能性がある。

Ashiato Syntax 自体は、この情報をサーバーに送信することを要求しない。

------------------------------------------------------------------------

# 25. Server / Client Responsibility

Ashiato Syntax は、現在位置をサーバーへ送信することを要求しない。

クライアントは、ローカルで現在位置と Ashiato の `g` を比較してもよい。

一方、サーバー側で位置判定を行う実装を禁止するものでもない。

以下は Syntax の責務ではない。

-   GPS取得
-   GPS精度
-   現在位置のサーバー送信
-   発見半径
-   Geohash cell との距離判定
-   cooldown
-   claim
-   owner
-   score
-   anti-cheat
-   ゲームルール
-   通知
-   UI
-   URL preview
-   quote / reply / repost
-   Markdown / MFM 等のSNS固有機能

------------------------------------------------------------------------

# 26. 時間条件の評価アルゴリズム

v1.0 evaluator は、概念的に以下の順序で評価する。

``` text
1. 現在の UTC datetime を取得する。

2. z があれば、その固定 UTC Offset を適用する。
   なければ z = 0 とする。

3. local_datetime を得る。

4. local_datetime から以下を得る。

   local_date
   local_weekday
   local_minute

5. d があれば local_date と比較する。

6. w があれば local_weekday と比較する。

7. t があれば local_minute と比較する。

8. s/e があれば current Unix minute と比較する。

9. すべての存在する field が true の場合、
   Ashiato は active とする。
```

論理的には、

``` text
Active =
    LocationMatch
    AND AbsoluteTimeMatch
    AND DateMatch
    AND WeekdayMatch
    AND TimeMatch
```

である。

ただし `LocationMatch` の具体的なアルゴリズムは Syntax では規定しない。

------------------------------------------------------------------------

# 27. Test Vectors

以下は v1.0 の代表的なテストケースである。

## 27.1 Basic

``` text
Input:
⟦as:1,g:9q8yyk⟧

Valid:
Yes

Canonical:
⟦as:1,g:9q8yyk⟧
```

------------------------------------------------------------------------

## 27.2 Zero offset

``` text
Input:
⟦as:1,g:9q8yyk,z:0⟧

Valid:
Yes

Canonical:
⟦as:1,g:9q8yyk⟧
```

------------------------------------------------------------------------

## 27.3 Positive offset

``` text
Input:
⟦as:1,g:9q8yyk,z:+f0⟧

Valid:
Yes

Canonical:
⟦as:1,g:9q8yyk,z:+f0⟧
```

------------------------------------------------------------------------

## 27.4 Negative offset

``` text
Input:
⟦as:1,g:9q8yyk,z:-8c⟧

Valid:
Yes

Canonical:
⟦as:1,g:9q8yyk,z:-8c⟧
```

------------------------------------------------------------------------

## 27.5 Zero with sign

``` text
Input:
⟦as:1,g:9q8yyk,z:+0⟧

Valid:
Yes

Canonical:
⟦as:1,g:9q8yyk⟧
```

``` text
Input:
⟦as:1,g:9q8yyk,z:-0⟧

Valid:
Yes

Canonical:
⟦as:1,g:9q8yyk⟧
```

------------------------------------------------------------------------

## 27.6 Date OR

``` text
Input:
⟦as:1,g:9q8yyk,d:0505.0101⟧

Valid:
Yes

Canonical:
⟦as:1,g:9q8yyk,d:0101.0505⟧
```

------------------------------------------------------------------------

## 27.7 Weekday OR

``` text
Input:
⟦as:1,g:9q8yyk,w:751⟧

Valid:
Yes

Canonical:
⟦as:1,g:9q8yyk,w:157⟧
```

------------------------------------------------------------------------

## 27.8 Date AND weekday

``` text
Input:
⟦as:1,g:9q8yyk,d:0101,w:67⟧

Meaning:
1月1日 AND (土曜日 OR 日曜日)
```

------------------------------------------------------------------------

## 27.9 Normal time range

``` text
Input:
⟦as:1,g:9q8yyk,t:9c-uo⟧

Meaning:
09:00 <= local_time < 18:00
```

------------------------------------------------------------------------

## 27.10 Cross-midnight

``` text
Input:
⟦as:1,g:9q8yyk,t:uo-a0⟧

Meaning:
18:00 <= local_time OR local_time < 06:00
```

------------------------------------------------------------------------

## 27.11 Cross-midnight + weekday

``` text
Input:
⟦as:1,g:9q8yyk,w:1,t:uo-a0⟧

Meaning:
local weekday == Monday
AND
local time is in 18:00〜24:00 or 00:00〜06:00
```

火曜日00:00〜06:00は match しない。

------------------------------------------------------------------------

## 27.12 Empty 24-hour range

``` text
Input:
⟦as:1,g:9q8yyk,t:0-0⟧

Valid:
No
```

------------------------------------------------------------------------

## 27.13 0-1439

`t` の start/end は Base36 で表現する。

10進の `1439` は Base36 では `13z` であるため、

``` text
Input:
⟦as:1,g:9q8yyk,t:0-13z⟧

Meaning:
00:00 <= local_time < 23:59
```

となる。

これは24時間ではない。24時間有効を表す場合は `t` を省略する。

------------------------------------------------------------------------

## 27.14 Absolute interval

``` text
Input:
⟦as:1,g:9q8yyk,s:100,e:200⟧

Meaning:
100 <= current_unix_minute < 200
```

------------------------------------------------------------------------

## 27.15 Invalid absolute interval

``` text
Input:
⟦as:1,g:9q8yyk,s:200,e:100⟧

Valid:
No
```

------------------------------------------------------------------------

## 27.16 Unknown extension

``` text
Input:
⟦as:1,g:9q8yyk,x-test:foo⟧

Valid:
Yes
```

v1 evaluator は `x-test` の意味を解釈しない。

------------------------------------------------------------------------

# 28. Canonicalization の例

入力：

``` text
⟦as:1,g:9q8yyk,w:751,d:0505.0101,z:+0,s:100,e:200,x-test:foo⟧
```

Canonical Form：

``` text
⟦as:1,g:9q8yyk,s:2s,e:5k,d:0101.0505,w:157,x-test:foo⟧
```

ここで、

-   `z:+0` → 省略
-   field order → `s,e,d,w,extension`
-   `d` → 昇順
-   `w` → 昇順
-   Base36 → 小文字

となる。

------------------------------------------------------------------------

# 29. 実装上の推奨構造

実装は以下の責務に分離することを推奨する。

``` text
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

特に、文字列を直接操作しながら意味判定する実装ではなく、一度 Semantic
Model に変換することを推奨する。

例：

``` text
Ashiato {
    version: 1
    geohash: "9q8yyk"
    utc_offset_minutes: 540
    start_unix_minute: ...
    end_unix_minute: ...
    dates: [...]
    weekdays: [...]
    time_range: ...
    extensions: [...]
}
```

これにより、

-   validation
-   evaluation
-   canonicalization
-   equality
-   hashing
-   test

を独立して実装できる。

------------------------------------------------------------------------

# 30. Semantic Equality

2つの Ashiato Syntax が Semantic Model 上同一である場合、それらは
semantic equivalent である。

例えば、

``` text
⟦as:1,g:9q8yyk⟧
```

と、

``` text
⟦as:1,g:9q8yyk,z:0⟧
```

は semantic equivalent。

また、

``` text
⟦as:1,g:9q8yyk,d:0505.0101,w:751⟧
```

と、

``` text
⟦as:1,g:9q8yyk,d:0101.0505,w:157⟧
```

も semantic equivalent。

Canonical Form を比較することで、v1.0 の semantic equivalence
を文字列比較として実装できる。

------------------------------------------------------------------------

# 31. Versioning

v1.0 は `as:1` を使用する。

将来 v2 が定義された場合、v2 は `as:2` を使用する。

v1 parser は、未知の major version を v1 Syntax
として解釈してはならない。

Minor revision によって v1
の意味論を変更する場合は、相互運用性を壊さないよう別途仕様として明示する。

------------------------------------------------------------------------

# 32. Non-Goals

Ashiato Syntax v1.0 は以下を目的としない。

-   SNS API の標準化
-   地図 API の標準化
-   GPS の標準化
-   位置検索アルゴリズムの標準化
-   距離計算の標準化
-   ゲームルールの標準化
-   所有権・Claim の標準化
-   ユーザー認証
-   暗号化
-   電子署名
-   URL scheme
-   SNS固有のUI
-   IANA Time Zone の表現
-   複雑な論理式

------------------------------------------------------------------------

# 33. まとめ

Ashiato Syntax v1.0 は、以下の最小モデルを採用する。

``` text
Location
    g

Absolute Time
    s
    e

Recurring Local Time
    z
    d
    w
    t
```

論理構造は、

``` text
fields = AND
values within a field = OR
```

である。

時間評価は、

``` text
UTC datetime
    ↓
fixed UTC offset (z)
    ↓
local datetime
    ├── local date      → d
    ├── local weekday   → w
    └── local time      → t
```

となる。

`g` は位置セルを表すが、発見距離やマッチング方法は規定しない。

`t` の日跨ぎは local datetime の日付を変更せず、`d` と `w`
は常に評価対象となる瞬間の local date / weekday を評価する。

Canonicalization は、

``` text
parse
→ validate
→ semantic model
→ canonical serialize
```

として定義し、同じ意味を持つ Syntax を同一の Canonical Form に変換する。

Ashiato Syntax
の責務は**「位置と時間条件を小さな文字列として記述すること」**までであり、発見体験やゲーム性はクライアント側に委ねる。

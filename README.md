# Ashiato Syntax Specification

**Version:** 1.0
**Status:** Draft

## 1. 概要

Ashiato Syntax は、SNSの投稿本文に位置情報と時間条件を埋め込むための軽量なマイクロシンタックスである。

Ashiato Syntax自体は特定のSNSやプロトコルに依存しない。

Misskey、Bluesky、Mastodonなど、投稿本文に任意の文字列を含められるサービスで利用できる。

Ashiato Syntaxは暗号化された位置情報ではない。`g` に含まれる位置情報は公開情報であり、第三者が復元できることを前提とする。

---

## 2. 基本構文

Ashiato Syntax v1の基本形は以下の通り。

```text id="5e5c6c"
⟦as:1,g:<geohash>[,<field>:<value>...]⟧
```

`as` と `g` は必須であり、順序も固定する。

```text id="k9t7f1"
as → g
```

`g` 以降のフィールドは任意であり、**順序は自由**とする。

現在定義されているフィールド：

```text id="5x6v4h"
s = start time
e = expiration time
d = date
w = weekday
t = time
```

---

## 3. Field Ordering

### 3.1 Parsing

パーサーは `g` より後のフィールドについて、**任意の順序を受け付けなければならない**。

例えば、以下は同じ意味を持つ。

```text id="0y2gk0"
⟦as:1,g:9q8yyk,s:abc,e:def,w:67,t:uo-a0⟧
```

```text id="v3m2u8"
⟦as:1,g:9q8yyk,t:uo-a0,w:67,e:def,s:abc⟧
```

パーサーはフィールドの順序に依存してはならない。

### 3.2 Generation

Ashiato Syntaxを生成する実装は、以下の正規順序を使用することを推奨する。

```text id="5m5p1m"
as → g → s → e → d → w → t
```

存在しない任意フィールドは省略する。

この順序は**生成時の正規形**であり、パーサーがこの順序を要求するものではない。

正規形を定義することで、将来的なハッシュ、署名、重複排除などへの利用を容易にする。

### 3.3 Duplicate Fields

同一キーを1つのAshiato Syntax内に複数回記述してはならない。

例えば以下は不正。

```text id="3p9xq1"
⟦as:1,g:9q8yyk,w:67,w:135⟧
```

---

## 4. Character Encoding

Ashiato Syntaxの構文部分にはASCII文字を使用し、開始・終了デリミタには以下のUnicode文字を使用する。

```text id="9w8h4b"
⟦  U+27E6 MATHEMATICAL LEFT WHITE SQUARE BRACKET
⟧  U+27E7 MATHEMATICAL RIGHT WHITE SQUARE BRACKET
```

構文全体はUTF-8で表現する。

デリミタはUnicode正規化によって別の文字へ変換してはならない。

### 4.1 区切り文字

```text id="1r8c7m"
,  フィールド間の区切り
.  同一フィールド内の複数値の区切り
-  時間範囲の開始・終了の区切り
:  キーと値の区切り
```

---

## 5. Base36 Encoding

`s`、`e`、`t` の値のエンコードにはBase36を使用する。

### 5.1 Alphabet

Ashiato Syntax v1では、Base36の文字セットを以下に固定する。

```text id="j5v1m3"
0123456789abcdefghijklmnopqrstuvwxyz
```

数字 `0-9` と小文字英字 `a-z` のみを使用する。

**大文字英字は正規形ではない。**

### 5.2 Leading Zero

Base36値の先頭に不要な `0` を付加しない。

例えば10進数35は、

```text id="9w4p7x"
z
```

と表現する。

```text id="9k5r1v"
0z
00z
```

とはしない。

0そのものは、

```text id="2j6m8p"
0
```

と表現する。

実装者は入力解析時に大文字を受け入れてもよいが、生成および正規化では小文字を使用する。

---

## 6. Location

### `g`

位置情報を示す。

値には標準的な **Geohash** をそのまま使用する。

```text id="3h7k9w"
g:9q8yyk
```

`g` は必須であり、**`as` の直後に置く**。

Ashiato Syntaxは独自の緯度・経度エンコード方式を定義しない。

### 6.1 Geohash Character Set

`g` の値には、標準的なGeohashで使用されるBase32 alphabetを使用する。

```text id="6m3r2v"
0123456789bcdefghjkmnpqrstuvwxyz
```

以下の文字は使用しない。

```text id="8x2n4q"
a
i
l
o
```

Geohashは**小文字のみを正規形**とする。

### 6.2 精度

Geohashの文字数によって公開位置の精度を決定する。

以下は目安であり、実際のセルサイズは緯度によって変化する。

```text id="4n8m1c"
5文字  → 数km級
6文字  → 1km級
7文字  → 100m級
8文字  → 数十m級
9文字  → 数m級
10文字 → 1m級
```

### 6.3 位置情報の公開

`g` は暗号化されない。

Geohashをデコードすることで、公開された位置セルを取得できる。

Ashiato Syntaxでは、位置情報の秘匿を目的とせず、**投稿者が公開位置の精度を選択できること**を基本方針とする。

---

## 7. Time Zone

Ashiato Syntax v1では、時間条件の解釈に使用するタイムゾーンを**UTCに固定する**。

対象となるフィールドは以下。

```text id="q8f2w1"
s
e
d
w
t
```

したがって、`d`、`w`、`t` は投稿地点のローカルタイムではなく、UTCを基準として評価する。

### 7.1 理由

位置情報の精度を任意に変更できるAshiatoにおいて、Geohashからタイムゾーンを推定すると、位置精度と時間条件が暗黙に結びついてしまう。

また、タイムゾーン境界付近では1つのGeohashセルが複数のタイムゾーンにまたがる可能性がある。

そのためv1では、解釈が一意になるUTCを採用する。

### 7.2 将来の拡張

将来的にローカルタイムを扱う必要が生じた場合は、拡張フィールドによってタイムゾーンを指定できるようにする可能性がある。

v1ではタイムゾーン指定フィールドを定義しない。

---

## 8. Start Time

### `s`

Ashiatoが有効になる絶対時刻を指定する。

値は以下の手順でエンコードする。

1. Unix timestampを取得する
2. 秒を60で割って切り捨てる
3. Base36へ変換する

定義：

```text id="5c8m4y"
s = Base36(floor(unix_timestamp / 60))
```

精度は1分。

`s` は任意。

---

## 9. Expiration Time

### `e`

Ashiatoが無効になる絶対時刻を指定する。

エンコード方式は `s` と同じ。

```text id="7h2v6n"
e = Base36(floor(unix_timestamp / 60))
```

精度は1分。

`e` は任意。

### 9.1 `s` と `e`

両方指定された場合、

```text id="1r6c9x"
s <= now <= e
```

を満たす期間のみAshiatoを有効とする。

`s` のみの場合は指定時刻以降に有効。

`e` のみの場合は指定時刻まで有効。

---

## 10. Date Condition

### `d`

毎年繰り返される特定の月日を指定する。

形式：

```text id="4m7q2v"
d:<MMDD>[.<MMDD>...]
```

1つ以上の月日を指定できる。

複数の月日は `.` で区切る。

例：

```text id="8f3k1m"
d:0915
```

毎年9月15日に有効。

```text id="2v9r5c"
d:0101.0505
```

毎年1月1日または5月5日に有効。

```text id="6n4w8p"
d:0101.0505.0915
```

毎年1月1日、5月5日、9月15日に有効。

### 10.1 月日の形式

各月日は必ず4桁の `MMDD` で表現する。

不正な月日（例：`1332`）は使用してはならない。

### 10.2 複数指定

同一の月日を複数回指定してはならない。

複数の月日は昇順に記述する。

```text id="7c5m2r"
d:0101.0505.0915
```

は正規形。

```text id="1v8n4k"
d:0915.0101.0505
```

は正規形ではない。

パーサーは順序を問わず受け入れてもよい。

### 10.3 年の扱い

`d` は年を指定しない。

指定された月日は**毎年繰り返される条件**として扱う。

特定の年だけ有効にしたい場合は `s` / `e` を使用する。

---

## 11. Weekday Condition

### `w`

曜日を指定する。

```text id="9m3k7x"
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

```text id="4p8v2n"
w:135
```

月・水・金曜日。

```text id="7r1c6m"
w:67
```

土・日曜日。

`w` は任意。

曜日は昇順に記述する。

同じ曜日を複数回指定してはならない。

`w` の値にはBase36エンコードを使用しない。

---

## 12. Time Condition

### `t`

1日の中でAshiatoが有効になる時間帯を指定する。

時刻は00:00からの経過分数として表現し、その整数をBase36へ変換する。

```text id="2k8m5v"
00:00 = 0
00:01 = 1
01:00 = 60
06:00 = 360
12:00 = 720
18:00 = 1080
23:59 = 1439
```

形式：

```text id="6r4n1p"
t:<start>-<end>
```

### 12.1 Base36の可変長表現

時刻のBase36表現は可変長とする。

不要な先頭の `0` は付加しない。

例：

```text id="3m7c9x"
00:00 → 0
01:00 → 1o
06:00 → a0
12:00 → k0
18:00 → uo
23:59 → zz
```

### 12.2 境界

時間条件は半開区間 `[start, end)` とする。

つまり、

```text id="5v2r8n"
start <= time < end
```

である。

終了時刻そのものは範囲に含まれない。

### 12.3 日跨ぎ

開始時刻が終了時刻より後の場合、時間帯は翌日にまたがるものとする。

```text id="8n1m4c"
t:uo-a0
```

は、

```text id="q7f5x2"
18:00〜翌06:00
```

を意味する。

内部的には、

```text id="6k3r9v"
time >= 18:00
OR
time < 06:00
```

として評価する。

### 12.4 同一時刻

開始時刻と終了時刻が同一となる指定は使用してはならない。

24時間有効の場合は `t` を省略する。

---

## 13. Condition Semantics

Ashiatoの有効性は、現在時刻に対する複数のpredicateとして評価する。

概念的には以下のように定義する。

```text id="4x8m2p"
Active(now) =
    LocationMatches
    AND StartCondition(now)
    AND ExpirationCondition(now)
    AND DateCondition(now)
    AND WeekdayCondition(now)
    AND TimeCondition(now)
```

存在しない任意フィールドの条件は常にtrueとして扱う。

### 13.1 フィールド間

異なるフィールドの条件は**AND**で結合する。

例えば、

```text id="7n5c1r"
d:0101,w:67,t:uo-a0
```

は、

```text id="4m8v2x"
DateCondition
AND WeekdayCondition
AND TimeCondition
```

となる。

### 13.2 同一フィールド内

同一フィールド内で複数の値が指定された場合、それらは**OR**で結合する。

例えば、

```text id="9r3k6m"
d:0101.0505
```

は、

```text id="6v1p8n"
date == 0101
OR
date == 0505
```

となる。

同様に、

```text id="2c7m4x"
w:67
```

は、

```text id="1n8r5v"
weekday == Saturday
OR
weekday == Sunday
```

となる。

### 13.3 複雑な論理式

Ashiato Syntax v1では、任意のOR/ANDを組み合わせた複雑な論理式はサポートしない。

条件構造は、

```text id="5x9k2m"
フィールド間 → AND
フィールド内 → OR
```

に限定する。

これにより、実装と仕様を単純に保つ。

---

## 14. Location Matching

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

## 15. Client-side Discovery

Ashiato Syntaxは、現在地をサーバーへ送信することを要求しない。

基本的なクライアント側処理は以下のようになる。

```text id="8m4r1c"
SNSから投稿を取得
        ↓
Ashiato Syntaxを抽出
        ↓
gをGeohashとして解釈
        ↓
端末の現在位置と比較
        ↓
Ashiatoを発見
```

現在位置そのものをSNSサーバーへ送信する必要はない。

---

## 16. Unknown Fields

将来的な拡張性を確保するため、v1で定義されていない未知のフィールドを構文上許容する。

例えば、

```text id="3p7x9m"
⟦as:1,g:9q8yyk,x:example⟧
```

の `x` はv1では未知のフィールドである。

v1実装は未知のフィールドを**構文上有効なものとして受け入れ、その意味を無視してよい**。

未知のフィールドの存在だけを理由としてAshiato Syntax全体を無効としてはならない。

ただし、`as` のバージョン自体が未知の場合は、そのバージョンの仕様を理解していない限り解釈してはならない。

例えば、

```text id="5k2n8r"
⟦as:2,g:9q8yyk⟧
```

の場合、v1実装はVersion 2の意味を解釈しない。

---

## 17. ABNF

Ashiato Syntax v1の基本的な文法を以下のABNFで定義する。

```abnf id="7c4m1v"
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

month-day = DIGIT DIGIT DIGIT DIGIT
weekday-value = 1*7DIGIT
base36 = 1*(DIGIT / %x61-7A)

geohash = 1*(%x30-39 / %x62-68 / %x6A-6B / %x6D-6E / %x70-7A)

extension-field = extension-key ":" extension-value
extension-key = 1*(ALPHA / DIGIT)
extension-value = 1*(ALPHA / DIGIT / "." / "-")
```

ABNFは構文上の構造を定義するものであり、`month-day` の実際の日付としての妥当性、Base36値の範囲、Geohashの意味論などは各フィールドの仕様に従う。

---

## 18. 本文中での位置

Ashiato Syntaxは、投稿本文の**末尾に配置することを推奨する**。

例：

```text id="9m2v5c"
この店、夜に来ると最高だった。

⟦as:1,g:9q8yyk,w:67,t:uo-a0⟧
```

Ashiato対応クライアントは、原則として投稿本文の末尾に自動的に追加する。

---

## 19. Multiple Ashiato

Ashiato Syntax v1では、**1投稿につき1つのAshiato Syntax**を基本とする。

複数のAshiato Syntaxが存在する場合の動作はv1では規定しない。

---

## 20. Examples

### 20.1 Basic

```text id="4r7m1x"
⟦as:1,g:9q8yyk⟧
```

指定された場所に恒久的なAshiatoを残す。

### 20.2 Future Activation

```text id="8c3v6n"
⟦as:1,g:9q8yyk,s:xxxxx⟧
```

指定された絶対時刻から有効。

### 20.3 Expiration

```text id="2m9k4p"
⟦as:1,g:9q8yyk,e:xxxxx⟧
```

指定された絶対時刻まで有効。

### 20.4 Multiple Dates

```text id="6x1r8c"
⟦as:1,g:9q8yyk,d:0101.0505.0915⟧
```

毎年1月1日、5月5日、9月15日に有効。

### 20.5 Weekday

```text id="3v7m2n"
⟦as:1,g:9q8yyk,w:67⟧
```

毎週土曜日・日曜日に有効。

### 20.6 Time

```text id="9p4c6m"
⟦as:1,g:9q8yyk,t:uo-a0⟧
```

毎日18:00〜翌06:00に有効。

### 20.7 Combined

```text id="5n8r1x"
⟦as:1,g:9q8yyk,s:xxxxx,e:xxxxx,d:0101.0505,w:67,t:uo-a0⟧
```

指定された期間内で、

* 1月1日または5月5日
* 土曜日または日曜日
* 18:00〜翌06:00

のすべてを満たす場合に有効。

---

## 21. Design Principles

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
13. **それ以降のフィールドは順序に依存しない**
14. **フィールド間はAND、同一フィールド内はORとする**
15. **時間条件はUTCで評価する**
16. **複雑な論理式をサポートせず、仕様を小さく保つ**

Ashiato Syntaxは、

> **「どこに、いつから、いつまで、どの月日・曜日・時間帯に有効なAshiatoなのか」**

を記述するための、SNS非依存の最小限の共通フォーマットを目指す。

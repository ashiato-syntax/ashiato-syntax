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

```text id="a6a3e2"
⟦as:1,g:<geohash>[,<field>:<value>...]⟧
```

`as` と `g` は必須であり、順序も固定する。

```text id="m0q2c5"
as → g
```

`g` 以降のフィールドは任意であり、**順序は自由**とする。

現在定義されているフィールド：

```text id="s5p0jd"
s = start time
e = expiration time
d = date
w = weekday
t = time
```

したがって、以下はすべて同じ意味を持つ。

```text id="h3q4q5"
⟦as:1,g:9q8yyk,s:xxxxx,e:xxxxx,w:67,t:uo-a0⟧
```

```text id="b6q5x0"
⟦as:1,g:9q8yyk,t:uo-a0,w:67,e:xxxxx⟧
```

```text id="f8v9j2"
⟦as:1,g:9q8yyk,w:67,t:uo-a0,s:xxxxx⟧
```

パーサーはフィールドの順序に依存してはならない。

### 2.1 正規形

Ashiato Syntaxを**生成する場合**は、フィールドを以下の順序で出力することを推奨する。

```text id="c4e8k7"
as → g → s → e → d → w → t
```

存在しない任意フィールドは省略する。

例えば、

```text id="d5u1x8"
⟦as:1,g:9q8yyk,e:xxxxx,w:67,t:uo-a0⟧
```

のように出力する。

この順序は**生成時の正規形**であり、パーサーがこの順序を要求するものではない。

---

## 3. Character Encoding

Ashiato Syntaxの構文部分にはASCII文字を使用し、開始・終了デリミタには以下のUnicode文字を使用する。

```text id="p1e7q2"
⟦  U+27E6 MATHEMATICAL LEFT WHITE SQUARE BRACKET
⟧  U+27E7 MATHEMATICAL RIGHT WHITE SQUARE BRACKET
```

キー、区切り文字、バージョン番号、および各エンコード値はASCII文字を使用する。

---

## 4. Syntax Identifier

### `as`

Ashiato Syntaxの識別子およびバージョンを示す。

```text id="q2w8m1"
as:1
```

`1` はAshiato Syntax Version 1を示す。

`as:1` は必須であり、**必ずSyntaxの先頭に置く**。

---

## 5. Location

### `g`

位置情報を示す。

値には標準的な **Geohash** をそのまま使用する。

```text id="v4c6n8"
g:9q8yyk
```

`g` は必須であり、**`as` の直後に置く**。

Ashiato Syntaxは独自の緯度・経度エンコード方式を定義しない。

### 5.1 Geohash Character Set

`g` の値には、標準的なGeohashで使用されるBase32 alphabetを使用する。

使用可能な文字は以下の32文字のみとする。

```text id="x7m2q4"
0123456789bcdefghjkmnpqrstuvwxyz
```

以下の文字は使用しない。

```text id="n5a9k1"
a
i
l
o
```

Geohashは**小文字のみを正規形**とする。

実装者は入力解析時に大文字を受け入れてもよいが、生成するAshiato Syntaxでは小文字を使用する。

### 5.2 精度

Geohashの文字数によって公開位置の精度を決定する。

Geohashのセルサイズは緯度によって変化するため、以下は目安である。

```text id="j8f3s6"
5文字  → 数km級
6文字  → 1km級
7文字  → 100m級
8文字  → 数十m級
9文字  → 数m級
10文字 → 1m級
```

実際のセルサイズおよび精度はGeohashの仕様に従う。

### 5.3 位置情報の公開

`g` は暗号化されない。

Geohashをデコードすることで、公開された位置セルを取得できる。

したがって、Ashiato Syntaxでは位置情報の秘匿を目的とせず、**投稿者が公開する位置精度を選択できること**を基本方針とする。

---

## 6. Base36 Encoding

`s`、`e`、`t` の値のエンコードにはBase36を使用する。

### 6.1 Alphabet

Ashiato Syntax v1では、Base36の文字セットを以下に固定する。

```text id="t4x6b8"
0123456789abcdefghijklmnopqrstuvwxyz
```

つまり、

* 数字 `0-9`
* 小文字英字 `a-z`

のみを使用する。

**大文字英字は正規形ではない。**

### 6.2 Leading Zero

Base36値の先頭に不要な `0` を付加しない。

例えば、10進数35は、

```text id="p7k2v5"
z
```

と表現する。

```text id="e3m8q1"
0z
00z
```

とはしない。

0そのものは、

```text id="w6h9c2"
0
```

と表現する。

### 6.3 大文字・小文字

生成されるAshiato Syntaxでは、Base36値を**小文字のみ**で表現する。

実装者は入力解析時に大文字を受け入れてもよいが、正規化時には小文字へ変換する。

---

## 7. Start Time

### `s`

Ashiatoが有効になる絶対時刻を指定する。

値は以下の手順でエンコードする。

1. Unix timestampを取得する
2. 秒を60で割って切り捨てる
3. Base36へ変換する

定義：

```text id="u1q4r8"
s = Base36(floor(unix_timestamp / 60))
```

精度は1分。

`s` は任意。

---

## 8. Expiration Time

### `e`

Ashiatoが無効になる絶対時刻を指定する。

エンコード方式は `s` と同じ。

```text id="n7v3m6"
e = Base36(floor(unix_timestamp / 60))
```

精度は1分。

`e` は任意。

### 8.1 `s` と `e`

両方指定された場合、

```text id="k4p8w2"
s <= 現在時刻 <= e
```

を満たす期間のみAshiatoを有効とする。

`s` のみの場合は指定時刻以降に有効。

`e` のみの場合は指定時刻まで有効。

---

## 9. Date Condition

### `d`

毎年繰り返される特定の月日を指定する。

形式：

```text id="r5x2j7"
d:MMDD
```

例：

```text id="f9c3v1"
d:0101
```

1月1日に有効。

```text id="m6q8s4"
d:1225
```

12月25日に有効。

`d` は任意。

年を指定しないため、毎年繰り返される条件として扱う。

特定の年だけ有効にしたい場合は `s` / `e` を使用する。

---

## 10. Weekday Condition

### `w`

曜日を指定する。

曜日は以下の数字で表現する。

```text id="q7n2x5"
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

```text id="v3k6m8"
w:135
```

月・水・金曜日。

```text id="h1q9r4"
w:67
```

土・日曜日。

`w` は任意。

曜日は昇順に記述する。

同じ曜日を複数回指定してはならない。

`w` の値にはBase36エンコードを使用しない。

---

## 11. Time Condition

### `t`

1日の中でAshiatoが有効になる時間帯を指定する。

時刻は00:00からの経過分数として表現し、その整数をBase36へ変換する。

```text id="b5w8q3"
00:00 = 0
00:01 = 1
01:00 = 60
06:00 = 360
12:00 = 720
18:00 = 1080
23:59 = 1439
```

開始時刻と終了時刻を `-` で区切る。

```text id="j2m7x9"
t:<start>-<end>
```

### 11.1 Base36の可変長表現

時刻のBase36表現は**可変長**とする。

不要な先頭の `0` は付加しない。

例：

```text id="p4v8n2"
00:00 → 0
01:00 → 1o
06:00 → a0
12:00 → k0
18:00 → uo
23:59 → zz
```

### 11.2 例

```text id="x6q3m8"
t:0-a0
```

00:00〜06:00。

```text id="c9r5w1"
t:k0-uo
```

12:00〜18:00。

```text id="n2h7v4"
t:uo-0
```

18:00〜翌00:00。

```text id="s8f1q6"
t:uo-a0
```

18:00〜翌06:00。

### 11.3 日付をまたぐ場合

開始時刻が終了時刻より後の場合、時間帯は翌日にまたがるものとする。

例えば、

```text id="m4x9k2"
t:uo-a0
```

は、

```text id="d7p3r5"
18:00〜翌06:00
```

を意味する。

### 11.4 `t` の精度

時間条件の精度は1分。

指定可能な時刻は、

```text id="q8v2n6"
00:00〜23:59
```

とする。

開始時刻と終了時刻が同一となる指定は使用しない。

24時間有効の場合は `t` を省略する。

---

## 12. 条件の組み合わせ

`s`、`e`、`d`、`w`、`t` が複数指定された場合、**すべての条件を満たした場合にAshiatoを有効とする。**

条件はANDで評価する。

例えば、

```text id="f5m8q2"
⟦as:1,g:9q8yyk,w:67,t:uo-a0⟧
```

は、

> 土曜日または日曜日、かつ18:00〜翌06:00

の時間帯に有効。

---

## 13. Field Ordering

### 13.1 Parsing

パーサーは `g` より後のフィールドについて、**任意の順序を受け付けなければならない**。

例えば、

```text id="a3v7n9"
⟦as:1,g:9q8yyk,s:abc,e:def,w:67,t:uo-a0⟧
```

と、

```text id="m2q6x8"
⟦as:1,g:9q8yyk,t:uo-a0,w:67,e:def,s:abc⟧
```

は同じ意味として解釈する。

### 13.2 Generation

Ashiato Syntaxを生成する実装は、以下の正規順序を使用することを推奨する。

```text id="v8k1p4"
as → g → s → e → d → w → t
```

これにより、同一内容のAshiato Syntaxを可能な限り同一の文字列表現にできる。

### 13.3 Duplicate Fields

同一キーを1つのAshiato Syntax内に複数回記述してはならない。

例えば以下は不正。

```text id="q5m9x3"
⟦as:1,g:9q8yyk,w:67,w:135⟧
```

---

## 14. 本文中での位置

Ashiato Syntaxは、投稿本文の**末尾に配置することを推奨する**。

例：

```text id="r7n2v5"
この店、夜に来ると最高だった。

⟦as:1,g:9q8yyk,w:67,t:uo-a0⟧
```

Ashiato Syntaxを生成するクライアントは、原則として投稿本文の末尾に自動的に追加する。

---

## 15. 複数Ashiato

Ashiato Syntax v1では、**1投稿につき1つのAshiato Syntax**を基本とする。

複数のAshiato Syntaxが存在する場合の動作はv1では規定しない。

---

## 16. Unknown Fields

Ashiato Syntaxは将来的な拡張を考慮し、未知のフィールドを許容する。

例えば、

```text id="c6q1m8"
⟦as:1,g:9q8yyk,x:example⟧
```

のように未知のキー `x` が存在した場合、v1対応クライアントはそのフィールドを無視してよい。

未知のフィールドは `as`、`g` を除く任意の位置に置くことができる。

ただし、`as` のバージョンが未知の場合はSyntax全体を解釈しない。

例えば、

```text id="n4v8p2"
⟦as:2,g:9q8yyk⟧
```

の場合、v1クライアントはVersion 2を解釈しない。

---

## 17. Client-side Location Matching

Ashiato Syntaxは、現在地をサーバーへ送信することを要求しない。

Ashiato対応クライアントは、例えば以下のように処理できる。

```text id="x2m7q5"
SNSから投稿を取得
        ↓
Ashiato Syntaxを抽出
        ↓
gをGeohashとしてデコード
        ↓
端末の現在位置と比較
        ↓
Ashiatoを発見
```

「何m以内で発見とするか」などのゲームルールはAshiato Syntaxでは規定しない。

そのため、同じAshiato Syntaxを、

* 現地探索ゲーム
* 地図上の口コミ
* 観光ガイド
* イベント
* 街歩き
* チェックイン

など、異なる用途で利用できる。

---

## 18. Examples

### 18.1 Basic

```text id="k5r8v2"
⟦as:1,g:9q8yyk⟧
```

指定された場所に恒久的なAshiatoを残す。

### 18.2 Future Activation

```text id="m3q7x9"
⟦as:1,g:9q8yyk,s:xxxxx⟧
```

指定された絶対時刻から有効。

### 18.3 Expiration

```text id="v6n2p4"
⟦as:1,g:9q8yyk,e:xxxxx⟧
```

指定された絶対時刻まで有効。

### 18.4 Specific Date

```text id="q8m1r5"
⟦as:1,g:9q8yyk,d:0915⟧
```

毎年9月15日に有効。

### 18.5 Weekday

```text id="x4k7n2"
⟦as:1,g:9q8yyk,w:67⟧
```

土曜日・日曜日に有効。

### 18.6 Time

```text id="p9v3m6"
⟦as:1,g:9q8yyk,t:uo-a0⟧
```

毎日18:00〜翌06:00に有効。

### 18.7 Combined

```text id="r2q6x8"
⟦as:1,g:9q8yyk,s:xxxxx,e:xxxxx,w:67,t:uo-a0⟧
```

指定された期間内で、土曜日・日曜日の18:00〜翌06:00のみ有効。

同じ内容を任意順序で記述することもできる。

```text id="n7m4v1"
⟦as:1,g:9q8yyk,t:uo-a0,e:xxxxx,w:67,s:xxxxx⟧
```

---

## 19. Design Principles

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
12. **必須情報を先頭に集約し、任意情報は順序に依存しない**

Ashiato Syntaxは、「どこに、いつから、いつまで、どの月日・曜日・時間帯に有効なAshiatoなのか」を記述するための、SNS非依存の最小限の共通フォーマットを目指す。

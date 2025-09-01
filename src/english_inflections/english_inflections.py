#! /usr/bin/python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Module to manage inflections of English words
#
# Copyright 2022 Mikio Hirabayashi
# Licensed under the Apache License, Version 2.0
#--------------------------------------------------------------------------------------------------

import collections
import re
import sys

_inflection_costs = {
  "np": 1.0,
  "vs": 1.0,
  "vc": 1.0,
  "vp": 1.0,
  "vx": 1.0,
  "ajc": 2.0,
  "ajs": 2.0,
  "avc": 2.0,
  "avs": 2.0,
  "a": 4.0,
}
_re_word_boundary = re.compile(r"\W+")
_re_ending_f = re.compile(r"(?i)(fe|f)$")
_re_ending_spirant = re.compile(r"(?i)(o|s|ch|sh|x)$")
_re_ending_vowel_y = re.compile(r"(?i)[aeiou]y$")
_re_ending_y = re.compile(r"(?i)y$")
_re_ending_ie = re.compile(r"(?i)ie$")
_re_ending_e = re.compile(r"(?i)e$")
_re_ending_long_vowel_consonant = re.compile(r"(?i)[aeiou]{2,}[^aeiouyx]$")
_re_ending_short_vowel_consonant = re.compile(r"(?i)[aeiou][^aeiouyx]$")
_re_ending_y = re.compile(r"(?i)y$")


class Inflector:
  """Utility to generate inflections of phrases and normalize inflected phrases.

コンストラクタはTSVデータベースファイル「english_inflections.tsv」を読み込みます。
InflectNoun、InflectVerb、InflectAdjective、InflectAdverb、およびInflectメソッドは
データベースを検索し、活用形のマップを返します。以下の属性を含みます。
- o: 原形
- np: 名詞複数形
- vs: 動詞単数形
- vc: 動詞現在分詞（別名：進行形/動名詞）
- vp: 動詞過去形
- vx: 動詞過去分詞
- ajc: 形容詞比較級
- ajs: 形容詞最上級
- avc: 副詞比較級
- avs: 副詞最上級
- _ph: デバッグ情報: データベースのフレーズエントリから取得した属性名
- _pi: デバッグ情報: フレーズのIDF（別名 -log(確率)）
- _th: デバッグ情報: データベースのトークンエントリから取得した属性名

各活用メソッドには「fbgen」パラメータがあります。これがtrueで、指定されたフレーズに対する適切な情報
が存在しない場合、活用形はヒューリスティックによって生成されます。
この目的で
GenerateNounPlural等を直接呼び出すことも可能です。

Searchメソッドは指定フレーズの原形を検索します。基本形とそのスコア（小さいほど良い）のリストを返します。
原語を検索するにはLookupPhraseInfoが有用です。
  """

  def __init__(self, data_path):
    """Initializes the object by loading the given data file.

    :param data_path: The path of the TSV file of inflection data.
    """
    self.word_dict = {}
    self.index = collections.defaultdict(list)
    with open(data_path) as input_file:
      for line in input_file:
        fields = line.strip().split("\t")
        if len(fields) < 2: continue
        orig = fields[0]
        attrs = {}
        uniq_infls = set()
        for field in fields:
          subfields = field.split(":")
          if len(subfields) != 2: continue
          label, value = subfields
          if label in _inflection_costs:
            infls = value.split(",")
            attrs[label] = infls
            for infl in set(infls):
              self.index[infl].append(orig)
          elif label == "i":
            attrs["i"] = float(value)
        self.word_dict[orig] = attrs

  def InflectNoun(self, phrase, fbgen=False):
    """Generates inflections of the given noun phrase.

    :param phrase: The base form string of a noun phrase.
    :param fbgen: If true, fallback generation is done.
    :return: The result attribute map.
    """
    ops = [(-1, 'np', GenerateNounPlural)]
    if not fbgen:
      ops = [(x[0], x[1], None) for x in ops]
    return self._InflectImpl(phrase, ops)

  def InflectVerb(self, phrase, fbgen=False):
    """Generates inflections of the given verb phrase.

    :param phrase: The base form string of a noun phrase.
    :param fbgen: If true, fallback generation is done.
    :return: The result attribute map.
    """
    ops = [(0, 'vs', GenerateVerbSingular), (0, 'vc', GenerateVerbPresentParticiple),
           (0, 'vp', GenerateVerbPast), (0, 'vx', GenerateVerbPastParticiple)]
    if not fbgen:
      ops = [(x[0], x[1], None) for x in ops]
    return self._InflectImpl(phrase, ops)

  def InflectAdjective(self, phrase, fbgen=False):
    """Generates inflections of the given adjective phrase.

    :param phrase: The base form string of an adjective phrase.
    :param fbgen: If true, fallback generation is done.
    :return: The result attribute map.
    """
    ops = [(0, 'ajc', GenerateAdjectiveComparative), (0, 'ajs', GenerateAdjectiveSuperative)]
    if not fbgen:
      ops = [(x[0], x[1], None) for x in ops]
    return self._InflectImpl(phrase, ops)

  def InflectAdverb(self, phrase, fbgen=False):
    """Generates inflections of the given adverb phrase.

    :param phrase: The base form string of an adverb phrase.
    :param fbgen: If true, fallback generation is done.
    :return: The result attribute map.
    """
    ops = [(-1, 'avc', GenerateAdverbComparative), (-1, 'avs', GenerateAdverbSuperative)]
    if not fbgen:
      ops = [(x[0], x[1], None) for x in ops]
    return self._InflectImpl(phrase, ops)

  def Inflect(self, phrase, fbgen=False):
    """Generates inflections of the given phrase as any part-of-speech.

    :param phrase: The base form string of a phrase.
    :param fbgen: If true, fallback generation is done.
    :return: The result attribute map.
    """
    ops = [(-1, 'np', GenerateNounPlural),
           (0, 'vs', GenerateVerbSingular), (0, 'vc', GenerateVerbPresentParticiple),
           (0, 'vp', GenerateVerbPast), (0, 'vx', GenerateVerbPastParticiple),
           (0, 'ajc', GenerateAdjectiveComparative), (0, 'ajs', GenerateAdjectiveSuperative),
           (-1, 'avc', GenerateAdverbComparative), (-1, 'avs', GenerateAdverbSuperative)]
    if not fbgen:
      ops = [(x[0], x[1], None) for x in ops]
    return self._InflectImpl(phrase, ops)

  def Search(self, phrase):
    """Searches for potential phrase information matching the given inflected phrase.

    :param phrase: The base or inflected form string of a phrase to look up.
    :return: A list of tuples. Each tuple has the word in the base form, its occurrence cost, and
    a list of form labels of the given phrase.
    """
    tokens = [x for x in _re_word_boundary.split(phrase.strip()) if x]
    orig_phrase = " ".join(tokens)
    matches = []
    uniq_bases = {orig_phrase}
    base_attrs = self.word_dict.get(orig_phrase)
    if base_attrs:
      idf = base_attrs.get("i") or 20.0
      matches.append((orig_phrase, idf, ["o"]))
    for base in self.index.get(orig_phrase) or []:
      if base in uniq_bases: continue
      base_attrs = self.word_dict.get(base)
      if not base_attrs: continue
      idf = base_attrs.get("i") or 20
      min_cost = 10
      form_labels = []
      for key, value in base_attrs.items():
        label_cost = _inflection_costs.get(key)
        if not label_cost: continue
        for infl in value:
          if infl == orig_phrase:
            min_cost = min(min_cost, label_cost)
            form_labels.append(key)
            break
          label_cost += 3.0
      matches.append((base, idf + min_cost, form_labels))
      uniq_bases.add(base)
    matches = sorted(matches, key=lambda x: (x[1], x[0]))
    if not matches and len(tokens) > 1:
      i = 0
      while i < len(tokens):
        token = tokens[i]
        bases = [token] + (self.index.get(token) or [])
        base_tokens = tokens.copy()
        for base in bases:
          base_tokens[i] = base
          base_phrase = " ".join(base_tokens)
          if base_phrase in uniq_bases: continue
          base_attrs = self.word_dict.get(base)
          if not base_attrs: continue
          idf = (base_attrs.get("i") or 20) + 20
          min_cost = 10
          form_labels = []
          for key, value in base_attrs.items():
            label_cost = _inflection_costs.get(key)
            if not label_cost: continue
            for infl in value:
              if infl == token:
                min_cost = min(min_cost, label_cost)
                form_labels.append(key)
                break
              label_cost += 3.0
          matches.append((base_phrase, idf + min_cost, form_labels))
          uniq_bases.add(base_phrase)
        i += 1
    matches = sorted(matches, key=lambda x: (x[1], x[0]))
    return matches

  def LookupPhraseInfo(self, phrase):
    """Looks up the given words in the dictionary.

    :param phrase: The base form string of a phrase.
    :return: The result attribute map, or None if there is no matching record.
    """
    attrs = self.word_dict.get(phrase)
    return attrs.copy() if attrs else None

  def _InflectImpl(self, phrase, ops):
    """Generates inflections of the given phrase with configurations.

    :param phrase: The base form string of a phrase.
    :param position: The position of the token to modify.
    :param ops: A list of focus positions, labels and generator functions.
    :return: The result attribute map.
    """
    tokens = [x for x in _re_word_boundary.split(phrase.strip()) if x]
    orig_phrase = " ".join(tokens)
    out_attrs = {"o": orig_phrase}
    dict_attrs = self.word_dict.get(orig_phrase) or {}
    phrase_labels = []
    for _, label, _ in ops:
      attr = dict_attrs.get(label)
      if attr:
        out_attrs[label] = attr.copy()
        phrase_labels.append(label)
    if phrase_labels:
      out_attrs["_ph"] = phrase_labels
    idf = dict_attrs.get("i")
    if idf:
      out_attrs["_pi"] = idf
    if len(phrase_labels) == len(ops): return out_attrs
    token_labels = []
    for position, label, generator in ops:
      if position >= 0:
        if position >= len(tokens): continue
      else:
        if abs(position) > len(tokens): continue
      base_token = tokens[position]
      copy_tokens = tokens.copy()
      dict_attrs = self.word_dict.get(base_token) or {}
      dict_values = dict_attrs.get(label)
      mod_phrases = []
      if dict_values:
        for dict_value in dict_values:
          copy_tokens[position] = dict_value
          mod_phrases.append(" ".join(copy_tokens))
        token_labels.append(label)
      elif not generator:
        continue
      else:
        copy_tokens[position] = generator(base_token)
        mod_phrases.append(" ".join(copy_tokens))
      out_attrs[label] = mod_phrases
    if token_labels:
      out_attrs["_th"] = token_labels
    return out_attrs


def GenerateNounPlural(word):
  """Generates the plural form of the given noun single word.

  :param word: The base form string of a noun single word.
  :return: The result string.
  """
  if _re_ending_f.search(word):
    return _re_ending_f.sub("ves", word)
  if _re_ending_spirant.search(word):
    return word + "es"
  if _re_ending_vowel_y.search(word):
    return word + "s"
  if _re_ending_y.search(word):
    return word[:-1] + "ies"
  return word + "s"


def GenerateVerbSingular(word):
  """Generates the third-person singular form of the given verb single word.

  :param word: The base form string of a verb single word.
  :return: The result string.
  """
  if _re_ending_spirant.search(word):
    return word + "es"
  if _re_ending_vowel_y.search(word):
    return word + "s"
  if _re_ending_y.search(word):
    return word[:-1] + "ies"
  return word + "s"


def GenerateVerbPresentParticiple(word):
  """Generates the present participle form of the given verb single word.

  :param word: The base form string of a verb single word.
  :return: The result string.
  """
  if _re_ending_ie.search(word):
    return word[:-2] + "ying"
  if _re_ending_e.search(word):
    return word[:-1] + "ing"
  if _re_ending_long_vowel_consonant.search(word):
    return word + "ing"
  if _re_ending_short_vowel_consonant.search(word):
    return word + word[-1] + "ing"
  return word + "ing"


def GenerateVerbPast(word):
  """Generates the past form of the given verb single word.

  :param word: The base form string of a verb single word.
  :return: The result string.
  """
  if _re_ending_vowel_y.search(word):
    return word + "ed"
  if _re_ending_y.search(word):
    return word[:-1] + "ied"
  if _re_ending_long_vowel_consonant.search(word):
    return word + "ed"
  if _re_ending_short_vowel_consonant.search(word):
    return word + word[-1] + "ed"
  if _re_ending_y.search(word):
    return word[:-1] + "ied"
  if _re_ending_e.search(word):
    return word + "d"
  return word + "ed"


def GenerateVerbPastParticiple(word):
  """Generates the past participle form of the given verb single word.

  :param word: The base form string of a verb single word.
  :return: The result string.
  """
  return GenerateVerbPast(word)


def GenerateAdjectiveComparative(word):
  """Generates the comparative form of the given adjective single word.

  :param word: The base form string of an adjective single word.
  :return: The result string.
  """
  if _re_ending_vowel_y.search(word):
    return word + "er"
  if _re_ending_y.search(word):
    return word[:-1] + "ier"
  if _re_ending_long_vowel_consonant.search(word):
    return word + "er"
  if _re_ending_short_vowel_consonant.search(word):
    return word + word[-1] + "er"
  if _re_ending_y.search(word):
    return word[:-1] + "ier"
  if _re_ending_e.search(word):
    return word + "r"
  return word + "er"


def GenerateAdjectiveSuperative(word):
  """Generates the superative form of the given adjective single word.

  :param word: The base form string of an adjective single word.
  :return: The result string.
  """
  if _re_ending_vowel_y.search(word):
    return word + "est"
  if _re_ending_y.search(word):
    return word[:-1] + "iest"
  if _re_ending_long_vowel_consonant.search(word):
    return word + "est"
  if _re_ending_short_vowel_consonant.search(word):
    return word + word[-1] + "est"
  if _re_ending_y.search(word):
    return word[:-1] + "iest"
  if _re_ending_e.search(word):
    return word + "st"
  return word + "est"


def GenerateAdverbComparative(word):
  """Generates the comparative form of the given adverb single word.

  :param word: The base form string of an adverb single word.
  :return: The result string.
  """
  return GenerateAdjectiveComparative(word)


def GenerateAdverbSuperative(word):
  """Generates the superative form of the given adverb single word.

  :param word: The base form string of an adverb single word.
  :return: The result string.
  """
  return GenerateAdjectiveSuperative(word)


def _ShowUsageAndDie():
  print("Usage:", file=sys.stderr)
  print("  english_inflections.py [--data path] [--fbgen] [--pos str] [--form str] query",
        file=sys.stderr)
  print("  english_inflections.py [--data path] [--search] query", file=sys.stderr)
  sys.exit(1)


def _RunTest(data_path):
  print("---- Generating funcitons ----")
  base_phrases = ["pen", "apple", "box", "catch", "pass", "path", "go", "die", "dye", "use",
                  "run", "pat", "wait", "beat", "smile", "cry", "study", "pay", "ski",
                  "hope", "hop", "bus", "city", "knife", "shelf",  "bar", "dumb",
                  "wise", "cute", "tall", "young", "long" "hot", "true", "happy"]
  infl_phrases = ["pens", "apples", "boxes", "caught", "passed", "paths", "gone", "dying",
                  "ran", "patting", "waiting", "beaten", "smiled", "cried", "studied", "payed",
                  "hoped", "hopping", "buses", "cities", "knives", "shelves",  "barring", "dumber",
                  "wiser", "cuter", "taller", "younger", "longer", "hottest", "truest", "happiest"]
  for phrase in base_phrases:
    print(phrase,
          GenerateNounPlural(phrase),
          GenerateVerbSingular(phrase),
          GenerateVerbPresentParticiple(phrase),
          GenerateVerbPast(phrase),
          GenerateAdjectiveComparative(phrase),
          GenerateAdjectiveSuperative(phrase))
  print("---- Inflect functions ----")
  inflector = Inflector(data_path)
  for phrase in base_phrases:
    print(phrase + ":", inflector.Inflect(phrase))
  print("---- Search function ----")
  for phrase in infl_phrases:
    print(phrase, inflector.Search(phrase))


def _RunInflection(data_path, query, is_fbgen, focus_pos, focus_form):
  inflector = Inflector(data_path)
  if focus_pos in ("n", "noun"):
    attrs = inflector.InflectNoun(query, is_fbgen)
  elif focus_pos in ("v", "verb"):
    attrs = inflector.InflectVerb(query, is_fbgen)
  elif focus_pos in ("a", "adj", "adjective"):
    attrs = inflector.InflectAdjective(query, is_fbgen)
  elif focus_pos in ("r", "adv", "adverb"):
    attrs = inflector.InflectAdverb(query, is_fbgen)
  else:
    attrs = inflector.Inflect(query, is_fbgen)
  if focus_form:
    value = attrs.get(focus_form)
    if value:
      for infl in value:
        print(infl)
  else:
    print(attrs)
    

def _RunSearch(data_path, query):
  inflector = Inflector(data_path)
  for base, score, labels in inflector.Search(query):
    print("{}\t{:.2f}\t{}".format(base, score, ",".join(labels)))


def _main():
  query_tokens = []
  is_test = False
  is_fbgen = False
  focus_pos = None
  focus_form = None
  is_search = False
  data_path = "english_inflections.tsv"
  i = 1
  while i < len(sys.argv):
    arg = sys.argv[i]
    if arg == "--data":
      data_path = sys.argv[i+1]
      i += 1
    elif arg == "--test":
      is_test = True
    elif arg == "--fbgen":
      is_fbgen = True
    elif arg == "--pos":
      i += 1
      focus_pos = sys.argv[i]
    elif arg == "--form":
      i += 1
      focus_form = sys.argv[i]
    elif arg == "--search":
      is_search = True
    elif arg.startswith("-"):
      _ShowUsageAndDie()
    else:
      query_tokens.append(arg)
    i += 1
  query = " ".join(query_tokens).strip()
  if is_test:
    _RunTest(data_path)
  elif is_search:
    if not query:
      _ShowUsageAndDie()
    _RunSearch(data_path, query)
  else:
    if not query:
      _ShowUsageAndDie()
    _RunInflection(data_path, query, is_fbgen, focus_pos, focus_form)


if __name__=="__main__":
  _main()

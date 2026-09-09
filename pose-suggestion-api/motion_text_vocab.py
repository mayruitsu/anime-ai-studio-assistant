"""モーションキャプションの単語を、自前の語彙表でID化する。

MDM本家はCLIP（大規模Web画像・テキストで学習済み、出処が不透明なAIモデル）でテキストを
条件付けに使っているが、これはCMUデータを選んだ動機（学習データの出処が怪しいAIには
頼らない）と矛盾する。データセットの語彙は数十語程度と小さいため、CLIPのような
汎用モデルは不要と判断し、学習データ（`generate_motion_labels.py`のキャプション）
だけから構築する自前の単語埋め込み（`nn.Embedding`をモデルと一緒にゼロから学習）を使う。
"""
PAD_TOKEN = "<pad>"


def tokenize(text: str) -> list[str]:
    return text.lower().replace(",", " ").split()


def build_vocab(texts: list[str]) -> list[str]:
    """出現した単語を頻度に依存せず決定的な順序（初出順）で並べ、語彙表を作る。"""
    vocab = [PAD_TOKEN]
    seen = {PAD_TOKEN}
    for text in texts:
        for word in tokenize(text):
            if word not in seen:
                seen.add(word)
                vocab.append(word)
    return vocab


def encode(text: str, vocab: list[str], max_len: int) -> list[int]:
    """テキストを語彙表のインデックス列（`max_len`にPAD_TOKENでパディング）に変換する。"""
    word_to_id = {word: i for i, word in enumerate(vocab)}
    ids = [word_to_id[word] for word in tokenize(text)]
    ids = ids[:max_len]
    return ids + [word_to_id[PAD_TOKEN]] * (max_len - len(ids))

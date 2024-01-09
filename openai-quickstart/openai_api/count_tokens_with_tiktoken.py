import tiktoken

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
print(encoding)

for encoding_name in ['cl100k_base', 'p50k_base', 'r50k_base']:
    for msg in ["tiktoken is great!"]:
        encoding = tiktoken.get_encoding(encoding_name)
        encode = encoding.encode(msg)
        print(encode)
        encode = encoding.decode(encode)
        print(encode)
        encode = [encoding.decode_single_token_bytes(token) for token in [83, 1609, 5963, 374, 2294, 0]]
        print(encode)

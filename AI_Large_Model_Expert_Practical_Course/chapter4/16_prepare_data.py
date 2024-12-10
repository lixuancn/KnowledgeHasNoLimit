import json
import os

# 16_data=https://drive.usercontent.google.com/download?id=1EdHUZIDpgcBoSqbjlfNKJ3b1t0XIUjbt&export=download&authuser=0&confirm=t&uuid=8062444c-9f4a-4d45-85b0-18c9433e2adb&at=APZUnTVIp-S0F7HyCRpkH7ILqqC3%3A1713443417964
import json
import os

class PrepareData():
    @staticmethod
    def prepare(root_dir):
        ds = []
        for dir_path, dir_names, file_names in os.walk(root_dir):
            for file_name in file_names:
                file_path = os.path.join(dir_path, file_name)
                with open(file_path, 'r') as file:
                    for line in file:
                        try:
                            text = json.loads(line)["text"]
                            ds.append(text)
                        except json.JSONDecodeError:
                            print("格式不正确")
        print(len(ds))
        with open('../excluded_folders/16_data/wiki_zh_sentence.txt', 'w') as file:
            for i in ds:
                file.write(i + '\n')
        return ds

data_set = PrepareData.prepare('/Users/bytedance/www/lanecn/KnowledgeHasNoLimit/AI_Large_Model_Expert_Practical_Course/excluded_folders/16_data/wiki_zh')
for item in data_set:
    print(item)
    break
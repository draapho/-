from najia.najia import Najia

if __name__ == "__main__":
    # 输入顺序为 [初, 二, 三, 四, 五, 上].
    params = [2, 0, 1, 1, 0, 0]
    result = Najia(1).compile(params=params, date="2025-12-06 00:00").render()
    print(result)

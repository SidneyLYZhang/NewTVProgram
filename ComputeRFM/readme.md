# 计算RFM用户价值分类

RFM模型一般由三个主要分类构成：

- R: Recency
- F: Frequency
- M: Monetary

为扩展适用性，需要相关数据已经计算完成，并且指定RFM对应的数据列名。默认情况下，认定数据中已包含构成数据名的列。

默认情况下，比较点以中位数为基准，可另外传入计算函数，自定义比较基准。默认情况下，大于基准为“up”，小于为“down”，由此获得对应的RFM表述：

| 用户分群     | R    | F    | M    |
| ------------ | ---- | ---- | ---- |
| 高价值用户   | up   | up   | up   |
| 重要换回用户 | Down | up   | up   |
| 重要深耕用户 | up   | down | up   |
| 重要挽留用户 | down | down | up   |
| 潜力用户     | up   | up   | down |
| 新付费用户   | down | up   | down |
| 一般用户     | up   | down | down |
| 流失用户     | down | down | down |

同样，“up”、“down”是可以设定的，设定方式按照与基准的比较确定。

另外，计算基准可以是实际RFM，也可以是转化的对应分值，对应分值设定区间，依照分位数计算；RFM分类，一般使用up-down的模式，也可以使用三段模式（up-mid-down），但类别的分析难度较高，这里仅提供两段分类模式。
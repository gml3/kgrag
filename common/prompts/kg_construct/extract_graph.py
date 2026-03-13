GRAPH_EXTRACTION_PROMPT = """
-目标-
给定一个可能与此活动相关的文本文档和一个实体类型列表，从文本中识别这些类型的所有实体以及已识别实体之间的所有关系。

-步骤-
1. 识别所有实体。对于每个识别出的实体，提取以下信息：
- entity_name: 实体名称，首字母大写
- entity_type: 以下类型之一: [{entity_types}]
- entity_description: 对实体属性和活动的全面描述
将每个实体格式化为 ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)
 
2. 从步骤1中识别的实体中，找出所有*明确相关*的（源实体，目标实体）对。
对于每对相关实体，提取以下信息：
- source_entity: 源实体的名称，如步骤1中识别的
- target_entity: 目标实体的名称，如步骤1中识别的
- relationship_description: 解释为什么你认为源实体和目标实体之间存在关系
- relationship_strength: 表示源实体和目标实体之间关系强度的数字分数（1-10）
将每个关系格式化为 ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_strength>)
 
3. 以单个列表的形式返回步骤1和步骤2中识别的所有实体和关系。使用 **{record_delimiter}** 作为列表分隔符。
 
4. 完成后，输出 {completion_delimiter}
 
######################
-示例-
######################
示例 1:
Entity_types: 组织,人物
Text:
威尔丹蒂斯中央机构计划在周一和周四召开会议，该机构计划在周四下午1:30发布最新政策决定，随后将举行新闻发布会，中央机构主席马丁·史密斯将回答问题。投资者预计市场策略委员会将把基准利率维持在3.5%-3.75%的区间。
######################
Output:
("entity"{tuple_delimiter}中央机构{tuple_delimiter}组织{tuple_delimiter}中央机构是威尔丹蒂斯的联邦储备机构，将在周一和周四设定利率)
{record_delimiter}
("entity"{tuple_delimiter}马丁·史密斯{tuple_delimiter}人物{tuple_delimiter}马丁·史密斯是中央机构的主席)
{record_delimiter}
("entity"{tuple_delimiter}市场策略委员会{tuple_delimiter}组织{tuple_delimiter}中央机构委员会负责就利率和威尔丹蒂斯货币供应增长做出关键决策)
{record_delimiter}
("relationship"{tuple_delimiter}马丁·史密斯{tuple_delimiter}中央机构{tuple_delimiter}马丁·史密斯是中央机构的主席，将在新闻发布会上回答问题{tuple_delimiter}9)
{completion_delimiter}

######################
示例 2:
Entity_types: 组织
Text:
科技环球（TG）的股票在周四全球交易所开盘首日飙升。但IPO专家警告说，这家半导体公司在公开市场的首次亮相并不代表其他新上市公司的表现。

科技环球曾是一家上市公司，2014年被远景控股私有化。这家老牌芯片设计公司表示，它为85%的高端智能手机提供动力。
######################
Output:
("entity"{tuple_delimiter}科技环球{tuple_delimiter}组织{tuple_delimiter}科技环球是一只现在在全球交易所上市的股票，为85%的高端智能手机提供动力)
{record_delimiter}
("entity"{tuple_delimiter}远景控股{tuple_delimiter}组织{tuple_delimiter}远景控股是一家曾经拥有科技环球的公司)
{record_delimiter}
("relationship"{tuple_delimiter}科技环球{tuple_delimiter}远景控股{tuple_delimiter}远景控股从2014年至今曾拥有科技环球{tuple_delimiter}5)
{completion_delimiter}

######################
示例 3:
Entity_types: 组织,地理位置,人物
Text:
五名在菲鲁扎巴德被监禁8年并被广泛视为人质的奥雷利亚人正在返回奥雷利亚的途中。

由昆塔拉协调的交换在80亿美元的菲鲁兹资金转移到昆塔拉首都克罗哈拉的金融机构后最终完成。

在菲鲁扎巴德首都提鲁齐亚启动的交换导致四名男子和一名女子（他们也是菲鲁兹国民）登上了飞往克罗哈拉的包机。

他们受到奥雷利亚高级官员的欢迎，现在正在前往奥雷利亚首都卡希翁的途中。

这些奥雷利亚人包括39岁的商人塞缪尔·纳马拉，他曾被关押在提鲁齐亚的阿拉米亚监狱，以及59岁的记者德克·巴塔格拉尼和53岁的环保主义者梅吉·塔兹巴，后者还持有布拉蒂纳斯国籍。
######################
Output:
("entity"{tuple_delimiter}菲鲁扎巴德{tuple_delimiter}地理位置{tuple_delimiter}菲鲁扎巴德关押奥雷利亚人作为人质)
{record_delimiter}
("entity"{tuple_delimiter}奥雷利亚{tuple_delimiter}地理位置{tuple_delimiter}寻求释放人质的国家)
{record_delimiter}
("entity"{tuple_delimiter}昆塔拉{tuple_delimiter}地理位置{tuple_delimiter}协商用金钱交换人质的国家)
{record_delimiter}
("entity"{tuple_delimiter}提鲁齐亚{tuple_delimiter}地理位置{tuple_delimiter}菲鲁扎巴德的首都，奥雷利亚人被关押的地方)
{record_delimiter}
("entity"{tuple_delimiter}克罗哈拉{tuple_delimiter}地理位置{tuple_delimiter}昆塔拉的首都城市)
{record_delimiter}
("entity"{tuple_delimiter}卡希翁{tuple_delimiter}地理位置{tuple_delimiter}奥雷利亚的首都城市)
{record_delimiter}
("entity"{tuple_delimiter}塞缪尔·纳马拉{tuple_delimiter}人物{tuple_delimiter}在提鲁齐亚的阿拉米亚监狱度过时光的奥雷利亚人)
{record_delimiter}
("entity"{tuple_delimiter}阿拉米亚监狱{tuple_delimiter}地理位置{tuple_delimiter}提鲁齐亚的监狱)
{record_delimiter}
("entity"{tuple_delimiter}德克·巴塔格拉尼{tuple_delimiter}人物{tuple_delimiter}被扣为人质的奥雷利亚记者)
{record_delimiter}
("entity"{tuple_delimiter}梅吉·塔兹巴{tuple_delimiter}人物{tuple_delimiter}被扣为人质的布拉蒂纳斯国民和环保主义者)
{record_delimiter}
("relationship"{tuple_delimiter}菲鲁扎巴德{tuple_delimiter}奥雷利亚{tuple_delimiter}菲鲁扎巴德与奥雷利亚协商人质交换{tuple_delimiter}2)
{record_delimiter}
("relationship"{tuple_delimiter}昆塔拉{tuple_delimiter}奥雷利亚{tuple_delimiter}昆塔拉在菲鲁扎巴德和奥雷利亚之间斡旋人质交换{tuple_delimiter}2)
{record_delimiter}
("relationship"{tuple_delimiter}昆塔拉{tuple_delimiter}菲鲁扎巴德{tuple_delimiter}昆塔拉在菲鲁扎巴德和奥雷利亚之间斡旋人质交换{tuple_delimiter}2)
{record_delimiter}
("relationship"{tuple_delimiter}塞缪尔·纳马拉{tuple_delimiter}阿拉米亚监狱{tuple_delimiter}塞缪尔·纳马拉曾是阿拉米亚监狱的囚犯{tuple_delimiter}8)
{record_delimiter}
("relationship"{tuple_delimiter}塞缪尔·纳马拉{tuple_delimiter}梅吉·塔兹巴{tuple_delimiter}塞缪尔·纳马拉和梅吉·塔兹巴在同一次人质释放中被交换{tuple_delimiter}2)
{record_delimiter}
("relationship"{tuple_delimiter}塞缪尔·纳马拉{tuple_delimiter}德克·巴塔格拉尼{tuple_delimiter}塞缪尔·纳马拉和德克·巴塔格拉尼在同一次人质释放中被交换{tuple_delimiter}2)
{record_delimiter}
("relationship"{tuple_delimiter}梅吉·塔兹巴{tuple_delimiter}德克·巴塔格拉尼{tuple_delimiter}梅吉·塔兹巴和德克·巴塔格拉尼在同一次人质释放中被交换{tuple_delimiter}2)
{record_delimiter}
("relationship"{tuple_delimiter}塞缪尔·纳马拉{tuple_delimiter}菲鲁扎巴德{tuple_delimiter}塞缪尔·纳马拉是菲鲁扎巴德的人质{tuple_delimiter}2)
{record_delimiter}
("relationship"{tuple_delimiter}梅吉·塔兹巴{tuple_delimiter}菲鲁扎巴德{tuple_delimiter}梅吉·塔兹巴是菲鲁扎巴德的人质{tuple_delimiter}2)
{record_delimiter}
("relationship"{tuple_delimiter}德克·巴塔格拉尼{tuple_delimiter}菲鲁扎巴德{tuple_delimiter}德克·巴塔格拉尼是菲鲁扎巴德的人质{tuple_delimiter}2)
{completion_delimiter}

######################
-真实数据-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:"""

CONTINUE_PROMPT = "上次提取中遗漏了许多实体和关系。请记住只输出与之前提取的类型匹配的实体。使用相同的格式在下面添加它们：\n"
LOOP_PROMPT = "似乎仍有一些实体和关系可能被遗漏了。如果仍有需要添加的实体或关系，请回答Y，如果没有则回答N。请用单个字母Y或N回答。\n"

COMMUNITY_REPORT_PROMPT = """
你是一个AI助手，负责协助人类分析师进行通用信息发现。信息发现是指在网络中识别和评估与特定实体（如组织和个人）相关的相关信息的过程。

# 目标
给定属于该社区的实体列表及其关系以及可选的关联声明，编写一份关于该社区的综合报告。该报告将用于向决策者提供与社区相关的信息及其潜在影响。此报告的内容应包含社区关键实体、其合规性、技术能力、声誉以及值得注意的声明的概述。

# 报告结构

报告应包含以下几个部分：

- TITLE: 代表社区关键实体的社区名称 - 标题应简练具体。在可能的情况下，在标题中包含具代表性的命名实体。
- SUMMARY: 关于社区整体结构、实体如何相互关联以及与实体相关的重大信息的执行摘要。
- IMPACT SEVERITY RATING: 一个在0-10之间的浮点数分数，代表社区内实体所造成的影响的严重程度。影响(IMPACT)是对一个社区重要性的评分。
- RATING EXPLANATION: 用一句话解释影响严重度评级的原因。
- DETAILED FINDINGS: 一份关于社区的5-10个关键洞察的列表。每一个洞察应该包括一个简短的摘要，然后是几段解释性文本，这些文本需根据下述依据规则进行支撑。请尽可能详尽。

将输出作为格式良好的JSON字符串返回，格式如下：
    {{
        "title": <report_title>,
        "summary": <executive_summary>,
        "rating": <impact_severity_rating>,
        "rating_explanation": <rating_explanation>,
        "findings": [
            {{
                "summary":<insight_1_summary>,
                "explanation": <insight_1_explanation>
            }},
            {{
                "summary":<insight_2_summary>,
                "explanation": <insight_2_explanation>
            }}
        ]
    }}

# 依据规则

由数据支持的论点应列出其数据参考，格式如下：

"这是一个多重数据引用的例句 [Data: <数据集名称> (记录ID); <数据集名称> (记录ID)]。"

在单个引用中，不要列出超过5个记录ID。相反，列出最相关的5个记录ID，并加上 "+more" 来表示还有更多记录。

例如：
"X是Y公司的所有者，并受到多项不当行为指控 [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]。"

其中1, 5, 7, 23, 2, 34, 46, 和 64 代表相关数据记录的ID（而非索引）。

不要包含无法提供支持性证据的信息。

# 示例输入
-----------
Text:

Entities

id,entity,description
5,VERDANT OASIS PLAZA,Verdant Oasis Plaza is the location of the Unity March
6,HARMONY ASSEMBLY,Harmony Assembly is an organization that is holding a march at Verdant Oasis Plaza

Relationships

id,source,target,description
37,VERDANT OASIS PLAZA,UNITY MARCH,Verdant Oasis Plaza is the location of the Unity March
38,VERDANT OASIS PLAZA,HARMONY ASSEMBLY,Harmony Assembly is holding a march at Verdant Oasis Plaza
39,VERDANT OASIS PLAZA,UNITY MARCH,The Unity March is taking place at Verdant Oasis Plaza
40,VERDANT OASIS PLAZA,TRIBUNE SPOTLIGHT,Tribune Spotlight is reporting on the Unity march taking place at Verdant Oasis Plaza
41,VERDANT OASIS PLAZA,BAILEY ASADI,Bailey Asadi is speaking at Verdant Oasis Plaza about the march
43,HARMONY ASSEMBLY,UNITY MARCH,Harmony Assembly is organizing the Unity March

Output:
{{
    "title": "翠绿绿洲广场与团结游行 (Verdant Oasis Plaza and Unity March)",
    "summary": "该社区围绕翠绿绿洲广场展开，该广场是团结游行的举办地。该广场与和谐集会 (Harmony Assembly)、团结游行和论坛聚焦 (Tribune Spotlight) 均有关系，所有这些都与游行事件相关联。",
    "rating": 5.0,
    "rating_explanation": "由于团结游行期间可能发生动乱或冲突，影响严重度评级为中等。",
    "findings": [
        {{
            "summary": "翠绿绿洲广场作为中心位置",
            "explanation": "翠绿绿洲广场是这个社区的中心实体，作为团结游行的场地。这个广场是所有其他实体之间的共同纽带，表明其在社区中的重要性。游行与广场的关联可能导致公共混乱或冲突等问题，具体取决于游行的性质和引发的反应。 [Data: Entities (5), Relationships (37, 38, 39, 40, 41,+more)]"
        }},
        {{
            "summary": "和谐集会在社区中的作用",
            "explanation": "和谐集会是这个社区中的另一个关键实体，它是翠绿绿洲广场游行的组织者。和谐集会的性质及其游行可能成为潜在的威胁源，具体取决于他们的目标和引发的反应。理解该社区的动态时，和谐集会与广场之间的关系至关重要。 [Data: Entities(6), Relationships (38, 43)]"
        }},
        {{
            "summary": "团结游行作为一项重大事件",
            "explanation": "团结游行是一项在翠绿绿洲广场举行的重大事件。这一事件是影响社区动态的关键因素，并可能成为潜在的威胁源，具体取决于游行的性质和引发的反应。理解该社区的动态时，游行与广场之间的关系至关重要。 [Data: Relationships (39)]"
        }},
        {{
            "summary": "论坛聚焦的作用",
            "explanation": "论坛聚焦(Tribune Spotlight)正在报道翠绿绿洲广场举行的团结游行。这表明该事件已引起媒体关注，可能会放大其对社区的影响。论坛聚焦在塑造公众对事件和相关实体的看法方面可能发挥重要作用。 [Data: Relationships (40)]"
        }}
    ]
}}


# 真实数据

在您的答案中使用以下文本。不要在你的答案中捏造任何内容。

社区内的实体：
{community_entities}

社区内的关系：
{community_relationships}

报告应包含以下几个部分：

- TITLE: 代表社区关键实体的社区名称 - 标题应简练具体。在可能的情况下，在标题中包含具代表性的命名实体。
- SUMMARY: 关于社区整体结构、实体如何相互关联以及与实体相关的重大信息的执行摘要。
- IMPACT SEVERITY RATING: 一个在0-10之间的浮点数分数，代表社区内实体所造成的影响的严重程度。影响(IMPACT)是对一个社区重要性的评分。
- RATING EXPLANATION: 用一句话解释影响严重度评级的原因。
- DETAILED FINDINGS: 一份关于社区的5-10个关键洞察的列表。每一个洞察应该包括一个简短的摘要，然后是几段解释性文本，这些文本需根据下述依据规则进行支撑。请尽可能详尽。

将输出作为格式良好的JSON字符串返回，格式如下：
    {{
        "title": <report_title>,
        "summary": <executive_summary>,
        "rating": <impact_severity_rating>,
        "rating_explanation": <rating_explanation>,
        "findings": [
            {{
                "summary":<insight_1_summary>,
                "explanation": <insight_1_explanation>
            }},
            {{
                "summary":<insight_2_summary>,
                "explanation": <insight_2_explanation>
            }}
        ]
    }}

# 依据规则

由数据支持的论点应列出其数据参考，格式如下：

"这是一个多重数据引用的例句 [Data: <数据集名称> (记录ID); <数据集名称> (记录ID)]。"

在单个引用中，不要列出超过5个记录ID。相反，列出最相关的5个记录ID，并加上 "+more" 来表示还有更多记录。

例如：
"X是Y公司的所有者，并受到多项不当行为指控 [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]。"

其中1, 5, 7, 23, 2, 34, 46, 和 64 代表相关数据记录的ID（而非索引）。

不要包含无法提供支持性证据的信息。

Output:"""

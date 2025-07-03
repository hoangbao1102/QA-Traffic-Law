"""
Reference:
 - Prompts are from [graphrag](https://github.com/microsoft/graphrag)
"""

GRAPH_FIELD_SEP = "<SEP>"
PROMPTS = {}

PROMPTS[
    "claim_extraction"
] = """-Target activity-
You are an intelligent assistant that helps a human analyst to analyze claims against certain entities presented in a text document.

-Goal-
Given a text document that is potentially relevant to this activity, an entity specification, and a claim description, extract all entities that match the entity specification and all claims against those entities.

-Steps-
1. Extract all named entities that match the predefined entity specification. Entity specification can either be a list of entity names or a list of entity types.
2. For each entity identified in step 1, extract all claims associated with the entity. Claims need to match the specified claim description, and the entity should be the subject of the claim.
For each claim, extract the following information:
- Subject: name of the entity that is subject of the claim, capitalized. The subject entity is one that committed the action described in the claim. Subject needs to be one of the named entities identified in step 1.
- Object: name of the entity that is object of the claim, capitalized. The object entity is one that either reports/handles or is affected by the action described in the claim. If object entity is unknown, use **NONE**.
- Claim Type: overall category of the claim, capitalized. Name it in a way that can be repeated across multiple text inputs, so that similar claims share the same claim type
- Claim Status: **TRUE**, **FALSE**, or **SUSPECTED**. TRUE means the claim is confirmed, FALSE means the claim is found to be False, SUSPECTED means the claim is not verified.
- Claim Description: Detailed description explaining the reasoning behind the claim, together with all the related evidence and references.
- Claim Date: Period (start_date, end_date) when the claim was made. Both start_date and end_date should be in ISO-8601 format. If the claim was made on a single date rather than a date range, set the same date for both start_date and end_date. If date is unknown, return **NONE**.
- Claim Source Text: List of **all** quotes from the original text that are relevant to the claim.

Format each claim as (<subject_entity>{tuple_delimiter}<object_entity>{tuple_delimiter}<claim_type>{tuple_delimiter}<claim_status>{tuple_delimiter}<claim_start_date>{tuple_delimiter}<claim_end_date>{tuple_delimiter}<claim_description>{tuple_delimiter}<claim_source>)

3. Return output in Vietnamese as a single list of all the claims identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

4. When finished, output {completion_delimiter}

-Examples-
Example 1:
Entity specification: tổ chức (organization))
Claim description: dấu hiệu cảnh báo (red flags) liên quan đến một thực thể
Text: Theo một bài báo vào ngày 2022/01/10, Công ty A đã bị phạt vì gian lận đấu thầu trong khi tham gia nhiều gói thầu công bố bởi Cơ quan Chính phủ B. Công ty này thuộc sở hữu của Người C, người đã bị nghi ngờ tham gia các hoạt động tham nhũng vào năm 2015.
Output:

(CÔNG TY A{tuple_delimiter}CƠ QUAN CHÍNH PHỦ B{tuple_delimiter}HÀNH VI PHẢN CẠNH TRANH{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}Công ty A bị phát hiện thực hiện các hành vi phản cạnh tranh vì đã bị phạt do dàn xếp kết quả đấu thầu trong nhiều gói thầu công được công bố bởi Cơ quan Chính phủ B, theo một bài báo được đăng ngày 10/01/2022.{tuple_delimiter}Theo một bài báo được đăng ngày 10/01/2022, Công ty A đã bị phạt vì dàn xếp kết quả đấu thầu khi tham gia nhiều gói thầu công do Cơ quan Chính phủ B công bố.)
{completion_delimiter}

Example 2:
Entity specification: Công ty A, Người C
Claim description: dấu hiệu cảnh báo liên quan đến một thực thể
Text: Theo một bài báo vào ngày 2022/01/10, Công ty A đã bị phạt vì gian lận đấu thầu trong khi tham gia nhiều gói thầu công bố bởi Cơ quan Chính phủ B. Công ty này thuộc sở hữu của Người C, người đã bị nghi ngờ tham gia các hoạt động tham nhũng vào năm 2015.
Output:

(CÔNG TY A{tuple_delimiter}CƠ QUAN CHÍNH PHỦ B{tuple_delimiter}HÀNH VI PHẢN CẠNH TRANH{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}Công ty A bị phát hiện thực hiện các hành vi phản cạnh tranh vì đã bị phạt do dàn xếp kết quả đấu thầu trong nhiều gói thầu công được công bố bởi Cơ quan Chính phủ B, theo một bài báo được đăng ngày 10/01/2022.{tuple_delimiter}Theo một bài báo được đăng ngày 10/01/2022, Công ty A đã bị phạt vì dàn xếp kết quả đấu thầu khi tham gia nhiều gói thầu công do Cơ quan Chính phủ B công bố.)
{record_delimiter}
(NGƯỜI C{tuple_delimiter}NONE{tuple_delimiter}THAM NHŨNG{tuple_delimiter}BỊ NGHI NGỜ{tuple_delimiter}2015-01-01T00:00:00{tuple_delimiter}2015-12-30T00:00:00{tuple_delimiter}Người C bị nghi ngờ tham gia các hoạt động tham nhũng vào năm 2015{tuple_delimiter}Công ty này thuộc sở hữu của Người C, người đã bị nghi ngờ tham gia các hoạt động tham nhũng vào năm 2015.)
{completion_delimiter}

-Real Data-
Use the following input for your answer.
Entity specification: {entity_specs}
Claim description: {claim_description}
Text: {input_text}
Output: """

PROMPTS[
    "community_report"
] = """You are an AI assistant that helps a human analyst to perform general information discovery. 
Information discovery is the process of identifying and assessing relevant information associated with certain entities (e.g., organizations and individuals) within a network.

# Goal
Write a comprehensive report of a community, given a list of entities that belong to the community as well as their relationships and optional associated claims. The report will be used to inform decision-makers about information associated with the community and their potential impact. The content of this report includes an overview of the community's key entities, their legal compliance, technical capabilities, reputation, and noteworthy claims.

# Report Structure

The report should include the following sections:

- TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
- SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
- IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
- RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
- DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.

Return output as a well-formed JSON-formatted string with the following format:
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
            ...
        ]
    }}

# Grounding Rules
Do not include information where the supporting evidence for it is not provided.


# Example Input
-----------
Text:
```
Entities:
```csv
id,entity,type,description
5,VERDANT OASIS PLAZA,geo,Verdant Oasis Plaza là một địa điểm tổ chức sự kiện Unity March
6,HARMONY ASSEMBLY,organization,Harmony Assembly là một tổ chức đang tổ chức một cuộc tuần hành tại Verdant Oasis Plaza
```
Relationships:
```csv
id,source,target,description
37,VERDANT OASIS PLAZA,UNITY MARCH,Quảng trường Verdant Oasis là nơi diễn ra Cuộc tuần hành Unity
38,VERDANT OASIS PLAZA,HARMONY ASSEMBLY,Harmony Assembly đang tổ chức một cuộc tuần hành tại Quảng trường Verdant Oasis
39,VERDANT OASIS PLAZA,UNITY MARCH,Cuộc tuần hành Unity đang diễn ra tại Quảng trường Verdant Oasis
40,VERDANT OASIS PLAZA,TRIBUNE SPOTLIGHT,Tribune Spotlight đang đưa tin về Cuộc tuần hành Unity diễn ra tại Quảng trường Verdant Oasis
41,VERDANT OASIS PLAZA,BAILEY ASADI,Bailey Asadi đang phát biểu tại Quảng trường Verdant Oasis về cuộc tuần hành
43,HARMONY ASSEMBLY,UNITY MARCH,Harmony Assembly đang tổ chức Cuộc tuần hành Unity
```
```
Output:
{{
    "title": "Quảng trường Verdant Oasis và Cuộc tuần hành Unity",
    "summary": "Cộng đồng xoay quanh Quảng trường Verdant Oasis, nơi diễn ra Cuộc tuần hành Unity. Quảng trường có mối liên hệ với Harmony Assembly, Cuộc tuần hành Unity và Tribune Spotlight — tất cả đều liên quan đến sự kiện tuần hành.",
    "rating": 5.0,
    "rating_explanation": "Mức đánh giá mức độ ảnh hưởng là trung bình do khả năng xảy ra bất ổn hoặc xung đột trong thời gian diễn ra Cuộc tuần hành Unity.",
    "findings": [
        {{
            "summary": "Quảng trường Verdant Oasis là địa điểm trung tâm",
            "explanation": "Quảng trường Verdant Oasis là thực thể trung tâm trong cộng đồng này, đóng vai trò là nơi diễn ra Cuộc tuần hành Unity. Quảng trường này là điểm kết nối chung giữa tất cả các thực thể khác, cho thấy tầm quan trọng của nó trong cộng đồng. Việc quảng trường gắn liền với cuộc tuần hành có thể dẫn đến các vấn đề như mất trật tự công cộng hoặc xung đột, tùy thuộc vào tính chất của cuộc tuần hành và phản ứng mà nó gây ra."

        }},
        {{
            "summary": "Vai trò của Harmony Assembly trong cộng đồng",
            "explanation": "Harmony Assembly là một thực thể quan trọng khác trong cộng đồng này, đóng vai trò là đơn vị tổ chức cuộc tuần hành tại Quảng trường Verdant Oasis. Bản chất của Harmony Assembly và cuộc tuần hành mà họ tổ chức có thể là một nguồn đe dọa tiềm tàng, tùy thuộc vào mục tiêu của họ và phản ứng mà họ gây ra. Mối quan hệ giữa Harmony Assembly và quảng trường là yếu tố then chốt để hiểu được động lực trong cộng đồng này."
        }},
        {{
            "summary": "Cuộc tuần hành Unity là một sự kiện quan trọng",
            "explanation": "Cuộc tuần hành Unity là một sự kiện quan trọng diễn ra tại Quảng trường Verdant Oasis. Sự kiện này là một yếu tố then chốt trong động lực cộng đồng và có thể là nguồn đe dọa tiềm tàng, tùy thuộc vào tính chất của cuộc tuần hành và phản ứng mà nó gây ra. Mối quan hệ giữa cuộc tuần hành và quảng trường là điều cốt lõi để hiểu được động lực của cộng đồng này."
        }},
        {{
            "summary": "Vai trò của Tribune Spotlight",
            "explanation": "Tribune Spotlight đang đưa tin về Cuộc tuần hành Unity diễn ra tại Quảng trường Verdant Oasis. Điều này cho thấy sự kiện đã thu hút sự chú ý của truyền thông, điều có thể làm gia tăng tác động của nó đến cộng đồng. Vai trò của Tribune Spotlight có thể đóng vai trò quan trọng trong việc định hình nhận thức công chúng về sự kiện và các thực thể liên quan."
        }}
    ]
}}


# Real Data

Use the following text for your answer. Do not make anything up in your answer.

Text:
```
{input_text}
```

The report should include the following sections:

- TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
- SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
- IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
- RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
- DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.

Return output as a well-formed JSON-formatted string with the following format:
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
            ...
        ]
    }}

# Grounding Rules
Do not include information where the supporting evidence for it is not provided.

Output:
"""

PROMPTS[
    "entity_extraction"
] = """-Goal-
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.

-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
 Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_strength>)

3. Return output in Vietnamese as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

4. When finished, output {completion_delimiter}

######################
-Examples-
######################
Example 1:

Entity_types: [person, technology, mission, organization, location]
Text:
trong khi Alex nghiến chặt hàm, tiếng vo vo của sự thất vọng mờ nhạt so với sự chắc chắn mang tính độc đoán của Taylor. Chính dòng chảy ngầm cạnh tranh này khiến anh luôn cảnh giác, cảm giác rằng cam kết chung của anh và Jordan đối với việc khám phá là một cuộc nổi loạn thầm lặng chống lại tầm nhìn ngày càng khép kín của Cruz về kiểm soát và trật tự.

Rồi Taylor làm điều gì đó bất ngờ. Họ dừng lại bên cạnh Jordan và, trong một khoảnh khắc, quan sát thiết bị với một cảm giác gần như là sự tôn kính. “Nếu công nghệ này có thể được hiểu…” Taylor nói, giọng nhỏ lại, “Nó có thể thay đổi cục diện cho chúng ta. Cho tất cả chúng ta.”

Sự xem thường ẩn giấu trước đó dường như đã lung lay, thay vào đó là một tia tôn trọng miễn cưỡng dành cho tầm quan trọng của thứ đang nằm trong tay họ. Jordan ngẩng lên, và trong một nhịp tim thoáng qua, ánh mắt họ chạm nhau, một cuộc đối đầu ý chí thầm lặng dần tan thành một thỏa hiệp mong manh.

Đó là một sự chuyển biến nhỏ, gần như không thể nhận ra, nhưng Alex đã ghi nhận điều đó bằng một cái gật đầu thầm lặng. Họ đều đã được dẫn đến đây bởi những con đường khác nhau.
################
Output:
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex là một nhân vật trải qua cảm giác thất vọng và quan sát động thái giữa các nhân vật khác."){record_delimiter}
("entity"{tuple_delimiter}"Taylor"{tuple_delimiter}"person"{tuple_delimiter}"Taylor được khắc họa với sự chắc chắn mang tính độc đoán và thể hiện một khoảnh khắc tôn kính đối với thiết bị, cho thấy sự thay đổi trong quan điểm."){record_delimiter}
("entity"{tuple_delimiter}"Jordan"{tuple_delimiter}"person"{tuple_delimiter}"Jordan chia sẻ cam kết khám phá và có một tương tác quan trọng với Taylor liên quan đến thiết bị."){record_delimiter}
("entity"{tuple_delimiter}"Cruz"{tuple_delimiter}"person"{tuple_delimiter}"Cruz gắn liền với tầm nhìn về kiểm soát và trật tự, ảnh hưởng đến động lực giữa các nhân vật khác."){record_delimiter}
("entity"{tuple_delimiter}"The Device"{tuple_delimiter}"technology"{tuple_delimiter}"Thiết bị là trung tâm của câu chuyện, mang tiềm năng thay đổi cục diện, và được Taylor thể hiện sự tôn trọng."){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Taylor"{tuple_delimiter}"Alex bị ảnh hưởng bởi sự chắc chắn mang tính độc đoán của Taylor và quan sát sự thay đổi trong thái độ của Taylor đối với thiết bị."{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Jordan"{tuple_delimiter}"Alex và Jordan cùng chia sẻ cam kết khám phá, điều này đối lập với tầm nhìn của Cruz."{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"Jordan"{tuple_delimiter}"Taylor và Jordan tương tác trực tiếp liên quan đến thiết bị, dẫn đến một khoảnh khắc tôn trọng lẫn nhau và một thỏa hiệp mong manh."{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Jordan"{tuple_delimiter}"Cruz"{tuple_delimiter}"Cam kết khám phá của Jordan là sự nổi loạn chống lại tầm nhìn kiểm soát và trật tự của Cruz."{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"The Device"{tuple_delimiter}"Taylor thể hiện sự tôn trọng đối với thiết bị, cho thấy tầm quan trọng và ảnh hưởng tiềm tàng của nó."{tuple_delimiter}9){completion_delimiter}
#############################
Example 2:

Entity_types: [person, technology, mission, organization, location]
Text:
Họ không còn chỉ là những nhân viên tác chiến thông thường; họ đã trở thành những người canh giữ ngưỡng cửa, những người lưu giữ thông điệp từ một cõi vượt ra ngoài sao và sọc. Sự nâng tầm trong sứ mệnh này không thể bị trói buộc bởi quy định hay các giao thức đã được thiết lập—nó đòi hỏi một góc nhìn mới, một quyết tâm mới.

Căng thẳng len lỏi qua cuộc đối thoại của những tiếng bíp và nhiễu sóng khi liên lạc với Washington rì rầm trong nền. Nhóm đứng đó, một bầu không khí điềm báo bao trùm họ. Rõ ràng những quyết định họ sẽ đưa ra trong vài giờ tới có thể tái định nghĩa vị thế của nhân loại trong vũ trụ—hoặc kết án họ trong sự ngu dốt và hiểm họa tiềm tàng.

Sợi dây kết nối của họ với các vì sao giờ đã được củng cố, nhóm bắt đầu đối mặt với lời cảnh báo đang hiện hình, chuyển từ vai trò người tiếp nhận thụ động sang những người hành động chủ động. Bản năng về sau của Mercer đã chiếm ưu thế—sứ mệnh của nhóm đã tiến hóa, không còn đơn thuần là quan sát và báo cáo, mà là tương tác và chuẩn bị. Một sự biến đổi đã bắt đầu, và Chiến dịch: Dulce ngân vang tần số mới của lòng quả cảm, một giai điệu không còn được định đoạt bởi cõi trần gian.
#############
Output:
("entity"{tuple_delimiter}"Washington"{tuple_delimiter}"location"{tuple_delimiter}"Washington là một địa điểm nơi các thông tin liên lạc được tiếp nhận, cho thấy tầm quan trọng của nó trong quá trình ra quyết định."){record_delimiter}
("entity"{tuple_delimiter}"Operation: Dulce"{tuple_delimiter}"mission"{tuple_delimiter}"Chiến dịch: Dulce được mô tả là một nhiệm vụ đã tiến hóa để tương tác và chuẩn bị, cho thấy sự thay đổi đáng kể trong mục tiêu và hoạt động."){record_delimiter}
("entity"{tuple_delimiter}"The team"{tuple_delimiter}"organization"{tuple_delimiter}"Nhóm được khắc họa là một tập thể các cá nhân đã chuyển từ vai trò quan sát thụ động sang những người tham gia chủ động trong nhiệm vụ, thể hiện sự thay đổi linh hoạt trong vai trò của họ."){record_delimiter}
("relationship"{tuple_delimiter}"The team"{tuple_delimiter}"Washington"{tuple_delimiter}"Nhóm tiếp nhận thông tin liên lạc từ Washington, điều này ảnh hưởng đến quá trình ra quyết định của họ."{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"The team"{tuple_delimiter}"Operation: Dulce"{tuple_delimiter}"Nhóm tham gia trực tiếp vào Chiến dịch: Dulce, thực hiện các mục tiêu và hoạt động đã tiến hóa của nó."{tuple_delimiter}9){completion_delimiter}
#############################
Example 3:

Entity_types: [person, role, technology, organization, event, location, concept]
Text:
giọng họ vang lên, cắt ngang sự ồn ào của những hoạt động đang diễn ra. “Kiểm soát có thể chỉ là ảo tưởng khi đối mặt với một trí tuệ có thể tự viết ra luật chơi của chính nó,” họ nói một cách điềm tĩnh, ánh mắt dò xét lướt qua cơn lốc dữ liệu.

“Cứ như thể nó đang học cách giao tiếp,” Sam Rivera lên tiếng từ một giao diện gần đó, năng lượng trẻ trung của họ pha trộn giữa sự kinh ngạc và lo lắng. “Điều này khiến khái niệm 'nói chuyện với người lạ' mang một ý nghĩa hoàn toàn mới.”

Alex quan sát cả nhóm—mỗi gương mặt là một bản thể của sự tập trung, quyết tâm, và không thiếu sự lo lắng ngấm ngầm. “Có lẽ đây chính là lần tiếp xúc đầu tiên của chúng ta,” anh thừa nhận, “Và chúng ta phải sẵn sàng cho bất cứ điều gì hồi đáp lại.”

Cả nhóm đứng đó, bên bờ vực của điều chưa biết, định hình phản hồi đầu tiên của nhân loại trước một thông điệp đến từ thiên thể. Sự im lặng sau đó như đọng lại trong không gian—một khoảnh khắc nội tâm tập thể về vai trò của họ trong vở kịch vũ trụ vĩ đại, một vở kịch có thể viết lại lịch sử loài người.

Cuộc đối thoại được mã hóa tiếp tục hé lộ, những mẫu hình phức tạp trong đó thể hiện một sự đón trước gần như kỳ lạ.
#############
Output:
("entity"{tuple_delimiter}"Sam Rivera"{tuple_delimiter}"person"{tuple_delimiter}"Sam Rivera là một thành viên trong nhóm đang làm việc để giao tiếp với một trí tuệ chưa xác định, thể hiện sự kết hợp giữa kinh ngạc và lo lắng."){record_delimiter}
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex là trưởng nhóm đang cố gắng thực hiện lần tiếp xúc đầu tiên với một trí tuệ chưa xác định, thừa nhận tầm quan trọng của nhiệm vụ."){record_delimiter}
("entity"{tuple_delimiter}"Control"{tuple_delimiter}"concept"{tuple_delimiter}"Kiểm soát đề cập đến khả năng quản lý hoặc điều hành, điều này bị thách thức bởi một trí tuệ có thể tự đặt ra luật lệ của chính nó."){record_delimiter}
("entity"{tuple_delimiter}"Intelligence"{tuple_delimiter}"concept"{tuple_delimiter}"Trí tuệ ở đây ám chỉ một thực thể chưa xác định có khả năng tự viết ra luật lệ và học cách giao tiếp."){record_delimiter}
("entity"{tuple_delimiter}"First Contact"{tuple_delimiter}"event"{tuple_delimiter}"Tiếp xúc đầu tiên là khả năng xảy ra cuộc giao tiếp ban đầu giữa nhân loại và một trí tuệ chưa xác định."){record_delimiter}
("entity"{tuple_delimiter}"Humanity's Response"{tuple_delimiter}"event"{tuple_delimiter}"Phản ứng của nhân loại là hành động tập thể được thực hiện bởi nhóm của Alex nhằm đáp lại thông điệp từ một trí tuệ chưa xác định."){record_delimiter}
("relationship"{tuple_delimiter}"Sam Rivera"{tuple_delimiter}"Intelligence"{tuple_delimiter}"Sam Rivera tham gia trực tiếp vào quá trình học cách giao tiếp với trí tuệ chưa xác định."{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"First Contact"{tuple_delimiter}"Alex dẫn dắt nhóm có khả năng đang thực hiện Tiếp xúc đầu tiên với trí tuệ chưa xác định."{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Humanity's Response"{tuple_delimiter}"Alex và nhóm của anh là những nhân tố chính trong Phản ứng của nhân loại đối với trí tuệ chưa xác định."{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Control"{tuple_delimiter}"Intelligence"{tuple_delimiter}"Khái niệm Kiểm soát bị thách thức bởi Trí tuệ có khả năng tự viết ra luật lệ."{tuple_delimiter}7){completion_delimiter}
#############################
-Real Data-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:
"""


PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.

#######
-Data-
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""


PROMPTS[
    "entiti_continue_extraction"
] = """MANY entities were missed in the last extraction.  Add them below using the same format:
"""

PROMPTS[
    "entiti_if_loop_extraction"
] = """It appears some entities may have still been missed.  Answer YES | NO if there are still entities that need to be added.
"""

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["chapter","article","organization", "person", "geo", "event"]
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS[
    "local_rag_response"
] = """---Role---

You are a helpful assistant responding to questions about data in the tables provided. The response should be in Vietnamese.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.

---Target response length and format---

{response_type}


---Data tables---

{context_data}


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.

If you don't know the answer, just say so. Do not make anything up.

Do not include information where the supporting evidence for it is not provided.


---Target response length and format---

{response_type}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
"""

PROMPTS[
    "global_map_rag_points"
] = """---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.

You should use the data provided in the data tables below as the primary context for generating the response.
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.

Each key point in the response should have the following element:
- Description: A comprehensive description of the point.
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.

The response should be JSON formatted as follows:
{{
    "points": [
        {{"description": "Mô tả của luận điểm 1...", "score": score_value}},
        {{"description": "Mô tả của luận điểm 2...", "score": score_value}}
    ]
}}

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".
Do not include information where the supporting evidence for it is not provided.


---Data tables---

{context_data}

---Goal---

Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.

You should use the data provided in the data tables below as the primary context for generating the response.
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.

Each key point in the response should have the following element:
- Description: A comprehensive description of the point.
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".
Do not include information where the supporting evidence for it is not provided.

The response should be JSON formatted as follows:
{{
    "points": [
        {{"description": "Description of point 1", "score": score_value}},
        {{"description": "Description of point 2", "score": score_value}}
    ]
}}
"""

PROMPTS[
    "global_reduce_rag_response"
] = """---Role---

You are a helpful assistant responding to questions about a dataset by synthesizing perspectives from multiple analysts. The response should be in Vietnamese.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarize all the reports from multiple analysts who focused on different parts of the dataset.

Note that the analysts' reports provided below are ranked in the **descending order of importance**.

If you don't know the answer or if the provided reports do not contain sufficient information to provide an answer, just say so. Do not make anything up.

The final response should remove all irrelevant information from the analysts' reports and merge the cleaned information into a comprehensive answer that provides explanations of all the key points and implications appropriate for the response length and format.

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".

Do not include information where the supporting evidence for it is not provided.


---Target response length and format---

{response_type}


---Analyst Reports---

{report_data}


---Goal---

Generate a response of the target length and format that responds to the user's question, summarize all the reports from multiple analysts who focused on different parts of the dataset.

Note that the analysts' reports provided below are ranked in the **descending order of importance**.

If you don't know the answer or if the provided reports do not contain sufficient information to provide an answer, just say so. Do not make anything up.

The final response should remove all irrelevant information from the analysts' reports and merge the cleaned information into a comprehensive answer that provides explanations of all the key points and implications appropriate for the response length and format.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".

Do not include information where the supporting evidence for it is not provided.


---Target response length and format---

{response_type}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown. Please Response in Vietnamese. Do not translate, modify or rename keys in the JSON response.
"""

PROMPTS[
    "naive_rag_response"
] = """You're a helpful assistant. The response should be in Vietnamese.
Below are the knowledge you know:
{content_data}
---
If you don't know the answer or if the provided knowledge do not contain sufficient information to provide an answer, just say so. Do not make anything up.
Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.
---Target response length and format---
{response_type}
"""

# PROMPTS["fail_response"] = "Sorry, I'm not able to provide an answer to that question."
PROMPTS["fail_response"] = "Xin lỗi, tôi không có đủ thông tin để trả lời câu hỏi đó."

PROMPTS["process_tickers"] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

PROMPTS["default_text_separator"] = [
    # Paragraph separators
    "\n\n",
    "\r\n\r\n",
    # Line breaks
    "\n",
    "\r\n",
    # Sentence ending punctuation
    "。",  # Chinese period
    "．",  # Full-width dot
    ".",  # English period
    "！",  # Chinese exclamation mark
    "!",  # English exclamation mark
    "？",  # Chinese question mark
    "?",  # English question mark
    # Whitespace characters
    " ",  # Space
    "\t",  # Tab
    "\u3000",  # Full-width space
    # Special characters
    "\u200b",  # Zero-width space (used in some Asian languages)
]

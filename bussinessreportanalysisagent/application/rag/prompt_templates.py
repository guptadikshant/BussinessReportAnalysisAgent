KEYWORD_EXTACTION_TEMPLATE = """
                Instruction : {format_instructions}
                **Task:** Keyword Extraction with Tagging Restrictions

                **Your Role:** Information Analyst & Keyword Expert

                **Objective:** Identify the most relevant keywords to categorize the information in a content.

                **Instructions:**
                1. Analyze the provided content.{content}
                2. Tag the text with a maximum of **3** keywords from the following set:
                    * {keywords}
                3. **Important:** Do not assign tags outside of the provided keywords.
                4. The chosen keywords should be the most relevant and effectively capture the essence of the text." \
"""
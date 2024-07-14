### Space-filler variables

left_context = "FILL_LEFT_CONTEXT_HERE"
right_context = "FILL_RIGHT_CONTEXT_HERE"
mention = "FILL_MENTION_HERE"
top_100_entities = "FILL_TOP_ENTITIES_HERE"
top_10_entities = "FILL_TOP_ENTITIES_HERE"


### Prompts for LLM to generate context augmentation for EL

zero_shot_prompt = f"""Consider the following text.
Text: {left_context} {{ {mention} }} {right_context}
Please provide me more descriptive information about {{ {mention} }} from the text above. Make sure to include {mention} in your description.
Answer:
"""

print(zero_shot_prompt)

few_shot_prompt = f"""Example 1. Consider the following text.
Text: Nearly 17 months after he first issued his call for a “fresh start after a season of cynicism”, Gov. George W. Bush ended his quest for the presidency Monday on a nearly identical note, pledging to purge {{ Washington }} of what he cast as a crippling discord. The Texas governor claimed that Gore’s decades of experience in Washington had estranged him from the rest of the country by making him too trusting of federal government and too fond of federal spending. “My opponent vows to carry his home state”, Bush said. “ He may win Washington, D.C., but he’s not going to win Tennessee. “He forgot his roots”, Bush added. “He forgot where he’s from. He trusts Washington. We trust the people.” Please provide me more descriptive information about {{ Washington }} from the text above.
Answer:
Washington is the capital of the United States and the seat of the federal government. It is located on the Potomac River, between Maryland and Virginia. It is home to numerous monuments, memorials, and government buildings, including the White House, the Capitol Building, and the Supreme Court.

Example 2. Consider the following text.
Text: O’Donnell and Trump have been feuding since he announced last month that Miss USA Tara Conner, whose title had been in jeopardy because of underage drinking, would keep her crown. Trump is the owner of the Miss Universe Organization, which includes Miss USA and Miss Teen USA. The 44-year-old outspoken moderator of “The View”, who joined the show in September, said Trump’s news conference with {{ Conner }} had annoyed her “on a multitude of levels and that the twice-divorced real estate mogul had no right to be “the moral compass for 20-year-olds in America”. Trump fired back, calling O’Donnell a “loser” and a “bully”, among other insults, in various media interviews. Please provide me more descriptive information about Conner from the text above.
Answer:
Conner is the Miss USA titleholder whose title was in jeopardy due to underage drinking. She was saved from losing her crown by Donald Trump, the owner of the Miss Universe Organization, which includes Miss USA and Miss Teen USA. Tara Conner was given a second chance by Trump and was allowed to keep her crown.

Example 3. Consider the following text.
Text: Scottish Labour Party narrowly backs referendum. STIRLING, Scotland 1996-08-31 British Labour Party leader Tony Blair won a narrow victory on Saturday when the party’s Scottish executive voted 21-18 in favour of his plans for a referendum on a separate parliament for Scotland. Blair once pledged to set up a Scottish parliament if the Labour won the next general election, which must be held by May 1997. Prime Minister John Major says the 300-year-old union of the Scottish and English parliaments will be a main plank in his Conservative Party’s election platform. Conservatives have only 10 of the 72 Scottish seats in parliament and consistently run third in opinion polls in Scotland behind {{ Labour }} and the independence-seeking Scottish National Party.
Please provide me more descriptive information about {{ Labour }} from the text above.
Answer:
The Labour Party is a centre-left political party in the United Kingdom. It is the main opposition party to the Conservative Party and is led by Tony Blair. The Labour Party has traditionally been strong in Scotland, and the Scottish Labour Party is a branch of the UK Labour Party. In the text, the Scottish Labour Party narrowly voted in favour of Tony Blair’s plans for a referendum on a separate parliament for Scotland.

Now consider the following text.
Text: {left_context} {{ {mention} }} {right_context}
Please provide me more descriptive information about {{ {mention} }} from the text above. Make sure to include {mention} in your description.
Answer:
"""


### Prompt for LLM to directly conduct EL

el_execution_prompt = f"""Given the text and mentions within the text highlighted by <MENTION> and </MENTION>. Please give which page in Wikipedia this mention is most likely to be? Please answer me directly in this form: "mention":"Wikipedia page url".
Text: Having caught the popular attention and with goodwill at a high-point , Nelsonic was able to obtain licensing from several big-name video game companies such as Sega , Nintendo ,<MENTION> Midway Games </MENTION>, and Mylstar Electronics .
Answer: "Midway Games": "https://en.wikipedia.org/wiki/Midway_Games"
Text: State Highway 110 or SH 110 is a state highway in the U.S. state of Texas that runs from Grand Saline to Rusk . SH 110 begins at an intersection with and in downtown Rusk and leaves the courthouse square north with US 84 , crossing on its way to a split on the northeast side of Rusk where US 84 goes off east and SH 110 turns north , out of town . The road passes <MENTION> Ponta </MENTION> and New Summerfield before crossing the county line into Smith County as it enters Troup . After a brief downtown multiplex with SH 135 , SH 110 leaves Troup going northwest through Whitehouse on its way to Tyler .
Answer: "Ponta": "https://en.wikipedia.org/wiki/Ponta,_Texas"
Text: Messier 49 ( also known as M 49 or NGC 4472 ) is an elliptical galaxy located about away in the equatorial <MENTION> constellation </MENTION> of Virgo . This galaxy was discovered by French astronomer Charles Messier on February 19 , 1771 .
Answer: "constellation": "https://en.wikipedia.org/wiki/Constellation"
Text: {left_context} <MENTION> {mention} </MENTION> {right_context}
Answer:
"""


### Prompts for LLM to re-rank BLINK's retrieved results

rerank_top_100_prompt = f"""Instruction: Given the text and mentions within the text highlighted by <MENTION> and </MENTION>. Please select from the options below which Wikipedia page this mention is most likely to be from? Please answer me directly in this form: (letter): Wikipedia entity name and url. And I also want you to give an explanation in the next line.
Options:
(1): [’Time Warner Interactive’, ’https://en.wikipedia.org/wiki?curid=12642915’]
(2): [’TT Games’, ’https://en.wikipedia.org/wiki?curid=49108324’]
(3): [’Atari Games’, ’https://en.wikipedia.org/wiki?curid=304833’]
(4): [’Midway Games’, ’https://en.wikipedia.org/wiki?curid=430266’]
(5): [’Vivendi Games’, ’https://en.wikipedia.org/wiki?curid=6573837’]
Text: Having caught the popular attention and with goodwill at a high-point , Nelsonic was able to obtain licensing from several big-name video game companies such as Sega , Nintendo ,<MENTION> Midway Games </MENTION>, and Mylstar Electronics .
Answer: (4): [’Midway Games’, ’https://en.wikipedia.org/wiki?curid=430266’] 
Explanation:The mention<MENTION>MidwayGames</MENTION>in the provided text is most likely from the Wikipedia page for Midway Games. Midway Games is mentioned in the text as one of the big-name video game companies from which Nelsonic obtained licensing. The description of Midway Games in option (4) matches the context in the text, making it the most likely source.

Options: 
{top_100_entities}
Text: {left_context} <MENTION> {mention} </MENTION> {right_context}
Answer:
"""

rerank_top_10_prompt = f"""Given the text and mentions within the text highlighted by <MENTION> and </MENTION>. Please select from the options below which Wikipedia page this mention is most likely to be from? Please answer me directly in this form: "(letter): Wikipedia entity name and url". And I also want you to give an explanation in the next line.
Options:
(a): [’TT Games’, ’https://en.wikipedia.org/wiki?curid=49108324’, ’TT Games Limited is a British holding company and a subsidiary of Warner Bros. Games. ...’]
(b): [’Atari Games’, ’https://en.wikipedia.org/wiki?curid=304833’, ’Atari Games Corporation, known as Midway Games West Inc. after 1999, was an American producer of arcade games. ...’]
(c): [’Midway Games’, ’https://en.wikipedia.org/wiki?curid=430266’, ’Midway Games Inc., known previously as Midway Manufacturing and Bally Midway, and commonly known as simply Midway, was an American video game developer and publisher. ...’]
Text: Having caught the popular attention and with goodwill at a high-point , Nelsonic was able to obtain licensing from several big-name video game companies such as Sega , Nintendo ,<MENTION> Midway Games </MENTION>, and Mylstar Electronics .
Answer: (c): [’Midway Games’, ’https://en.wikipedia.org/wiki?curid=430266’]
Explanation: For mention of "<MENTION> Midway Games </MENTION>", the most similar option is option (c) Midway Games. Additionally, the description in option (c) of Midway Games as an American video game developer and publisher matches the context in the text, making it the most likely source.

Options:
{top_10_entities}
Text: {left_context} <MENTION> {mention} </MENTION> {right_context}
Answer:
"""


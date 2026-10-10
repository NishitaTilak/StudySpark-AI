import json
import textwrap

import requests

import streamlit as st

from html import escape

# =========================================================

# 1. PAGE CONFIGURATION

# =========================================================

st.set_page_config(

    page_title="StudySpark | Learning Missions",

    page_icon="🪐",

    layout="wide",

    initial_sidebar_state="expanded",

)

OLLAMA_URL = "http://localhost:11434/api/generate"

OLLAMA_MODEL = "llama3.2:3b"

# =========================================================

# 2. DESIGN

# =========================================================

st.markdown(textwrap.dedent("""

<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

.stApp {

    background: #F7F7FC;

    color: #22233B;

    font-family: 'DM Sans', sans-serif;

}

h1, h2, h3, h4 {

    color: #22233B !important;

    font-family: 'Space Grotesk', sans-serif !important;

}

p, li, label, .stMarkdown, .stText, .stCaption {

    color: #292943;

}

[data-testid="stSidebar"] {

    background: #20213D;

}

[data-testid="stSidebar"] * {

    color: #FFFFFF;

}

.hero {

    background: linear-gradient(120deg, #27264B, #5145A5);

    color: white;

    padding: 32px;

    border-radius: 22px;

    margin: 8px 0 24px;

}

.hero h1 {

    color: white !important;

    font-size: 38px;

}

.hero p {

    color: #E5E3FF;

}

.eyebrow {

    color: #D0CAFF;

    font-weight: 700;

    letter-spacing: 2px;

    font-size: 12px;

}

.metric {

    background: white;

    border: 1px solid #E9E8F4;

    padding: 18px;

    border-radius: 16px;

}

.metric-number {

    font-size: 27px;

    font-weight: 700;

    color: #5145A5;

}

.muted {

    color: #666680 !important;

    font-size: 14px;

}

.lesson-explanation {

    background: white;

    color: #22233B;

    padding: 24px;

    border-radius: 16px;

    border-left: 6px solid #5145A5;

    font-size: 17px;

    line-height: 1.8;

    margin: 12px 0;

}

div.stButton > button,

div[data-testid="stFormSubmitButton"] > button {

    background: #2563EB !important;

    color: white !important;

    border: 1px solid #1D4ED8 !important;

    border-radius: 10px !important;

    min-height: 44px;

    font-weight: 700;

}

div.stButton > button *,

div[data-testid="stFormSubmitButton"] > button * {

    color: white !important;

}

div.stButton > button:hover,

div[data-testid="stFormSubmitButton"] > button:hover {

    background: #1D4ED8 !important;

}

div[data-baseweb="input"] input,

div[data-baseweb="textarea"] textarea {

    background: white !important;

    color: #22233B !important;

    -webkit-text-fill-color: #22233B !important;

    border-radius: 10px;

}

div[data-testid="stRadio"] label {

    background: white;

    color: #22233B !important;

    border: 1px solid #E0DDF1;

    border-radius: 10px;

    padding: 10px 12px;

    margin-bottom: 5px;

}

div[data-testid="stRadio"] label p,

div[data-testid="stRadio"] label span {

    color: #22233B !important;

}

div[data-testid="stRadio"] label:hover {

    border-color: #7669CF;

    background: #F3F1FF;

}

div[data-testid="stAlert"] p {

    color: inherit;

}

hr {

    border-color: #E9E8F4;

}

</style>

"""), unsafe_allow_html=True)

# =========================================================

# 3. SESSION STATE

# =========================================================

defaults = {

    "lesson": None,

    "lesson_topic": "",

    "lesson_level": "",

    "missions_completed": 0,

    "best_score": 0,

    "selected_level": "Beginner",

    "selected_mode": "🔍 Understand",

    "quiz_submitted": False,

    "quiz_answers": {},

    "quiz_score": 0,

    "quiz_percentage": 0,

    "quiz_attempt": 0,

    "mission_id": 0,

    "mission_finished": False,

    "practice_checked": {},

    "ai_error": "",

    "reflection_saved": "",

}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# Built-in lessons work on computers that do not have Ollama installed.
# The sample lesson path is instant and does not contact any local AI service.
OFFLINE_LESSONS = {
    "python": {
        "Beginner": {
            "title": "Python Fundamentals",
            "explanation": "Python is a programming language used to give instructions to a computer. Its readable syntax makes it friendly for beginners. A variable stores a value, such as a name or number. The print() function displays information, while input() collects information from a user. Conditions let a program choose between actions. Loops repeat actions without writing the same instruction many times. For example, a for loop can display the numbers from 1 to 5. Start by understanding each statement and predicting its output before running it.",
            "points": ["Variables give names to values, such as age = 20. The name can be used later instead of typing the value again.", "The print() function displays text or calculated results. Strings can be written inside single or double quotes.", "Input from input() arrives as text. Convert it with int() or float() when you need to perform numeric calculations.", "An if/else statement chooses an action based on whether a condition is true. Indentation identifies the code inside each branch.", "A loop repeats a block of code. Use for when iterating over a sequence or range, and while when repetition depends on a condition."],
            "questions": [
                ("Which function displays output?", ["input()", "print()", "type()", "range()"], "print()", "print() displays text or values on the screen."),
                ("Which symbol starts an assignment?", ["==", "=", "!=", ">"], "=", "A single equals sign assigns a value to a variable."),
                ("What type does input() return by default?", ["Integer", "Float", "String", "Boolean"], "String", "input() returns the entered text as a string."),
                ("Which keyword checks a condition?", ["for", "if", "def", "import"], "if", "The if statement runs a block when its condition is true."),
                ("Which loop is commonly used with range(5)?", ["for", "switch", "case", "class"], "for", "A for loop can iterate through the values produced by range().")
            ],
            "challenge_questions": [
                ("What is printed by x = 4; print(x + 3)?", ["4", "7", "43", "x + 3"], "7", "The value 3 is added to the integer 4."),
                ("What is the value of 9 // 2?", ["4.5", "4", "1", "18"], "4", "Floor division returns the whole-number quotient."),
                ("Which condition checks whether n is even?", ["n / 2 == 0", "n % 2 == 0", "n // 2 == 0", "n + 2 == 0"], "n % 2 == 0", "An even integer has remainder zero when divided by 2."),
                ("How many times does range(1, 4) iterate?", ["2", "3", "4", "5"], "3", "The values are 1, 2, and 3; the stop value is excluded."),
                ("What does a function's return statement do?", ["Displays text only", "Sends a value back to the caller", "Repeats a loop", "Reads keyboard input"], "Sends a value back to the caller", "return provides a result to the code that called the function.")
            ],
            "related": ["Python data types", "Conditions and loops", "Functions"]
        },
        "Intermediate": {
            "title": "Python Control Flow and Data Handling",
            "explanation": "Python programs combine data, control flow, and reusable operations. Assignment binds a name to an object, while expressions evaluate to values. Conditions can combine comparisons with and, or, and not. Iteration over ranges, strings, and collections avoids manual repetition. Functions encapsulate logic and can accept parameters or return results. Be careful when input is converted because invalid text can raise ValueError. For example, validating a number before processing it prevents a simple input mistake from crashing a program. Clear variable names and small functions make debugging easier.",
            "points": ["Names refer to objects rather than acting as permanently typed boxes. Reassignment can bind a name to a different object.", "Comparison expressions such as == and >= produce Boolean values. Combine conditions with and/or when multiple requirements must be checked.", "for loops iterate over iterable objects; while loops continue while a condition remains true. Make sure a while-loop condition can eventually become false.", "Functions separate a task into a reusable unit. Parameters receive inputs, and return communicates a result to the caller.", "Exceptions such as ValueError can occur during conversions. Use validation or targeted try/except blocks to handle expected bad input."],
            "questions": [
                ("What does `range(2, 6)` produce when iterated?", ["2, 3, 4, 5", "2, 3, 4, 5, 6", "1, 2, 3, 4, 5", "3, 4, 5, 6"], "2, 3, 4, 5", "The start is included and the stop value is excluded."),
                ("What is the result type of `5 > 2`?", ["int", "str", "bool", "list"], "bool", "A comparison evaluates to True or False."),
                ("Which statement sends a result back from a function?", ["print", "return", "input", "pass"], "return", "return provides the function's result to its caller."),
                ("Which exception may `int('hello')` raise?", ["KeyError", "ValueError", "IndexError", "ImportError"], "ValueError", "The text cannot be parsed as an integer."),
                ("Which loop directly iterates over list items?", ["for item in items", "if item in items", "def item in items", "try item in items"], "for item in items", "A for loop obtains each item from the iterable.")
            ],
            "challenge_questions": [
                ("What is printed by `print(bool([]))`?", ["True", "False", "None", "Error"], "False", "An empty list is falsy in Python."),
                ("If `x = 10`, what is `x % 3`?", ["0", "1", "2", "3"], "1", "Ten divided by three leaves a remainder of one."),
                ("Why use `return` instead of only `print()` in a reusable function?", ["It stores every result globally", "The caller can use the returned value", "It automatically repeats the function", "It converts every value to text"], "The caller can use the returned value", "A returned result can be assigned, tested, or passed to another function."),
                ("What happens if a `while` loop's condition never becomes false and there is no break?", ["It runs once", "It may run indefinitely", "It becomes a for loop", "Python skips the body"], "It may run indefinitely", "The loop continues while its condition stays true."),
                ("Which is the safest way to handle a possibly invalid integer input?", ["Assume all input is valid", "Catch every error silently", "Validate input or catch ValueError", "Convert the input to a list"], "Validate input or catch ValueError", "Targeted validation or exception handling handles expected conversion failures.")
            ],
            "related": ["List and dictionary operations", "Exception handling", "Function design"]
        },
        "Advanced": {
            "title": "Python Semantics and Robust Program Design",
            "explanation": "Reliable Python code depends on understanding object references, evaluation rules, iteration protocols, and error boundaries. Assignment binds a name to an object; it does not automatically copy mutable objects. Boolean operators short-circuit and may return operands rather than normalized Boolean values. Iterators allow data to be processed incrementally, while generators can avoid materializing large collections. Functions should have clear contracts, predictable return values, and controlled side effects. Exception handling should target failures that can be recovered from rather than masking programming defects. For example, processing a large file line by line limits memory use. Test edge cases such as empty collections, invalid input, and boundary values.",
            "points": ["Python variables are references to objects. Aliasing matters when two names refer to the same mutable list or dictionary.", "Short-circuit evaluation can skip later expressions. This is useful for guarded access, but expression order must remain clear.", "Iterators produce values on demand, and generators can reduce peak memory usage for large streams of data.", "A function contract should define accepted inputs, output behavior, and possible exceptions. Small, testable functions are easier to reason about.", "Robust error handling catches specific expected exceptions and preserves useful diagnostics. Broad silent exception handling can conceal defects."],
            "questions": [
                ("After `a = []; b = a; b.append(1)`, what is `a`?", ["[]", "[1]", "None", "An error"], "[1]", "Both names refer to the same mutable list."),
                ("What does short-circuit evaluation mean?", ["Every operand always runs", "Evaluation may stop once the result is determined", "All values become strings", "Expressions are evaluated in reverse"], "Evaluation may stop once the result is determined", "Boolean operators can avoid evaluating later operands when unnecessary."),
                ("Why can a generator help process a huge dataset?", ["It always sorts data", "It yields values incrementally", "It duplicates all rows", "It disables exceptions"], "It yields values incrementally", "Generators can avoid storing the entire output sequence at once."),
                ("Which design is preferable for expected conversion failure?", ["Catch ValueError near conversion", "Catch BaseException everywhere", "Ignore all errors", "Restart the computer"], "Catch ValueError near conversion", "Targeted handling avoids hiding unrelated programming errors."),
                ("What is the main purpose of a function contract?", ["Specify behavior and expectations", "Increase indentation", "Prevent all exceptions", "Make every variable global"], "Specify behavior and expectations", "A contract clarifies valid inputs and expected outputs or failures.")
            ],
            "challenge_questions": [
                ("What is the effect of `b = a` when `a` is a list?", ["It always deep-copies a", "Both names refer to the same list", "It converts a to a tuple", "It freezes the list"], "Both names refer to the same list", "Assignment creates another reference, not an automatic copy."),
                ("Which approach is most memory-efficient for a large line-oriented file?", ["Read the whole file into one string", "Iterate through the file line by line", "Create three copies of every line", "Convert the file to one giant list first"], "Iterate through the file line by line", "Streaming processes records without retaining the entire file in memory."),
                ("Why is `except Exception: pass` risky?", ["It guarantees correct output", "It may hide unexpected failures", "It catches only ValueError", "It validates the input"], "It may hide unexpected failures", "Silently swallowing errors makes defects difficult to detect."),
                ("What is the benefit of a generator expression over building a large list immediately?", ["It can compute items lazily", "It guarantees parallel execution", "It removes type checking", "It stores more duplicate data"], "It can compute items lazily", "Lazy iteration computes values as they are requested."),
                ("A function mutates a list argument. What should its contract make clear?", ["That mutation is impossible", "Its side effects on the passed object", "That all arguments become integers", "That the caller cannot access the list"], "Its side effects on the passed object", "Mutation affects the shared object and should be documented or avoided.")
            ],
            "related": ["Iterators and generators", "Mutable object references", "Testing and exception design"]
        }
    },
    "photosynthesis": {
        "Beginner": {
            "title": "Photosynthesis: How Plants Make Food",
            "explanation": "Photosynthesis is the process plants use to make sugar using light energy. Most of the process happens in leaves, inside structures called chloroplasts. Plants take in carbon dioxide from the air and water through their roots. Chlorophyll helps capture light energy. Using that energy, the plant makes glucose, a kind of sugar, and releases oxygen. Sunlight is the energy source, not a material ingredient. A simple way to remember the inputs is carbon dioxide, water, and light. Photosynthesis supports plant growth and supplies oxygen to the environment.",
            "points": ["Leaves collect light and exchange gases through tiny openings called stomata. These features help the plant obtain what it needs.", "Chlorophyll is a green pigment that absorbs light energy. This is why many leaves look green.", "Water is absorbed by roots and transported through the plant. It supplies material needed for the process.", "Carbon dioxide enters leaves from the air. Plants use its carbon to build sugar molecules.", "Glucose stores chemical energy and supports growth. Oxygen is released as a by-product of photosynthesis."],
            "questions": [
                ("What energy source powers photosynthesis?", ["Moonlight only", "Sunlight", "Soil", "Oxygen"], "Sunlight", "Light energy powers the process."),
                ("Which gas do plants take in for photosynthesis?", ["Carbon dioxide", "Oxygen", "Helium", "Hydrogen"], "Carbon dioxide", "Carbon dioxide provides carbon used to make sugars."),
                ("Which pigment helps absorb light?", ["Hemoglobin", "Chlorophyll", "Keratin", "Melanin"], "Chlorophyll", "Chlorophyll absorbs light energy."),
                ("What sugar is made during photosynthesis?", ["Glucose", "Salt", "Starch gas", "Nitrogen"], "Glucose", "Glucose is a sugar produced using the captured energy."),
                ("Which gas is released as a by-product?", ["Carbon dioxide", "Oxygen", "Methane", "Neon"], "Oxygen", "Oxygen is released during photosynthesis.")
            ],
            "challenge_questions": [
                ("A plant is kept in darkness for a long time. Which input is missing?", ["Light energy", "Carbon dioxide", "Water", "Minerals"], "Light energy", "Without light, photosynthesis cannot capture the energy it requires."),
                ("Why are leaves useful for photosynthesis?", ["They contain chloroplasts and exchange gases", "They absorb all soil minerals directly", "They produce sunlight", "They remove all water from roots"], "They contain chloroplasts and exchange gases", "Leaves contain photosynthetic cells and gas-exchange structures."),
                ("If a plant receives water and light but very little carbon dioxide, what is limited?", ["A required raw material", "The plant's need for gravity", "The production of sunlight", "The presence of chlorophyll in every root"], "A required raw material", "Carbon dioxide is a necessary input to build sugars."),
                ("Which statement best describes oxygen in photosynthesis?", ["It is the main energy source", "It is released as a by-product", "It is converted into sunlight", "It replaces glucose"], "It is released as a by-product", "Oxygen is released while the plant makes sugar."),
                ("Why does photosynthesis matter beyond the plant itself?", ["It supports food webs and adds oxygen", "It removes all carbon from Earth", "It makes plants independent of water", "It stops cellular respiration"], "It supports food webs and adds oxygen", "Sugars support ecosystems and oxygen is released to the environment.")
            ],
            "related": ["Plant cells", "Food chains", "Cellular respiration"]
        },
        "Intermediate": {
            "title": "Photosynthesis: Inputs, Outputs, and Light Capture",
            "explanation": "Photosynthesis converts light energy into chemical energy stored in carbohydrates. In plants, light-dependent reactions occur in thylakoid membranes, where absorbed light helps produce ATP and NADPH and water is split, releasing oxygen. The Calvin cycle occurs in the stroma and uses ATP and NADPH to incorporate carbon dioxide into organic molecules. The two stages are linked: products of the light reactions power carbon fixation. Light intensity, carbon dioxide concentration, and temperature can affect the rate. A limiting factor is the condition that most restricts the current rate. This framework explains why increasing one input may not help if another factor is limiting.",
            "points": ["Chloroplasts contain thylakoid membranes and stroma, which host different stages of photosynthesis. Location helps explain the division of work.", "Light-dependent reactions convert captured light energy into ATP and NADPH. Water splitting releases oxygen.", "The Calvin cycle uses ATP and NADPH to incorporate carbon dioxide into organic molecules. It does not directly require photons in each reaction.", "A limiting factor restricts the rate when other conditions are adequate. The limiting factor can change as conditions change.", "Photosynthesis rate is affected by light, carbon dioxide, and temperature. Very high temperatures can disrupt enzyme activity."],
            "questions": [
                ("Where do light-dependent reactions take place?", ["Thylakoid membranes", "Nucleus", "Cytosol only", "Cell wall"], "Thylakoid membranes", "The photosystems and electron transport chain are in thylakoid membranes."),
                ("What does the Calvin cycle use from the light reactions?", ["ATP and NADPH", "Oxygen and glucose only", "DNA and RNA", "Cellulose and starch"], "ATP and NADPH", "These molecules provide energy and reducing power."),
                ("Which process releases oxygen during photosynthesis?", ["Splitting of water", "Absorption of glucose", "Nitrogen fixation", "Fermentation"], "Splitting of water", "Water oxidation releases oxygen in the light reactions."),
                ("What is a limiting factor?", ["A factor restricting the current rate", "A factor that is always irrelevant", "The final product only", "A type of chloroplast"], "A factor restricting the current rate", "The limiting factor is the condition that most constrains the rate."),
                ("Which gas supplies carbon for carbohydrate synthesis?", ["Carbon dioxide", "Oxygen", "Argon", "Neon"], "Carbon dioxide", "Carbon dioxide is incorporated into organic molecules.")
            ],
            "challenge_questions": [
                ("Light intensity rises but photosynthesis rate does not. What may explain this?", ["Another factor is limiting", "The plant no longer needs carbon", "Light becomes a carbohydrate", "Chloroplasts turn into roots"], "Another factor is limiting", "Carbon dioxide, temperature, or another condition may now constrain the rate."),
                ("Why are ATP and NADPH important to the Calvin cycle?", ["They supply energy and reducing power", "They act as pigments", "They form the leaf stomata", "They absorb carbon dioxide directly from air"], "They supply energy and reducing power", "The cycle uses them to drive carbon fixation and reduction."),
                ("A plant's stomata close during drought. Which direct effect can restrict photosynthesis?", ["Less carbon dioxide enters", "More sunlight is created", "Water becomes carbon dioxide", "Oxygen becomes chlorophyll"], "Less carbon dioxide enters", "Closed stomata reduce gas exchange, limiting CO2 uptake."),
                ("Why can extremely high temperature lower photosynthesis?", ["Photosynthetic enzymes can lose function", "Chlorophyll becomes soil", "Carbon dioxide stops being a gas", "Light energy disappears"], "Photosynthetic enzymes can lose function", "High temperatures can impair enzymes and other cellular processes."),
                ("If carbon dioxide is increased while light is already limiting, what is likely?", ["Little or no rate increase from CO2 alone", "The rate must double", "Water is no longer needed", "Oxygen becomes the only input"], "Little or no rate increase from CO2 alone", "Increasing a non-limiting factor may not raise the rate.")
            ],
            "related": ["Light-dependent reactions", "Calvin cycle", "Limiting factors"]
        },
        "Advanced": {
            "title": "Photosynthesis: Bioenergetics and Rate Limitations",
            "explanation": "Photosynthesis couples photochemical energy capture to carbon assimilation. Photosystems in thylakoid membranes drive electron transfer, proton-gradient formation, ATP synthesis, and NADPH production; oxidation of water replenishes electrons and releases oxygen. The Calvin–Benson cycle uses ATP and NADPH to reduce fixed carbon, while RuBisCO catalyzes carbon fixation and can also react with oxygen. That oxygenase activity contributes to photorespiration, whose cost depends on environmental conditions and plant adaptations. Net carbon gain therefore depends on light, CO2 availability, temperature, stomatal conductance, and biochemical capacity. C3, C4, and CAM pathways differ in how they manage CO2 delivery and water loss. Understanding the limiting step is essential when interpreting experiments or predicting plant productivity.",
            "points": ["Photosystems drive electron transport and help establish a proton motive force. ATP synthase uses this gradient to make ATP.", "NADPH carries reducing power from the light reactions into carbon assimilation. ATP and NADPH requirements constrain the Calvin cycle.", "RuBisCO catalyzes CO2 fixation but can also oxygenate RuBP. Photorespiration can reduce net carbon gain under some conditions.", "C4 and CAM plants use different strategies to concentrate or temporally separate CO2 fixation. These adaptations can improve water-use efficiency in particular environments.", "Observed photosynthetic rate reflects interacting biochemical and environmental limits. Experiments should control variables and distinguish gross from net carbon exchange."],
            "questions": [
                ("What powers ATP synthesis in chloroplasts?", ["A proton gradient across thylakoid membranes", "Direct conversion of glucose to DNA", "Oxygen binding to RuBisCO", "Water entering the nucleus"], "A proton gradient across thylakoid membranes", "ATP synthase uses the proton motive force generated by electron transport."),
                ("What competing activity can RuBisCO perform?", ["Oxygenation of RuBP", "Synthesis of chlorophyll from oxygen", "Splitting glucose in mitochondria only", "Transport of water through xylem"], "Oxygenation of RuBP", "RuBisCO can catalyze oxygenation, contributing to photorespiration."),
                ("What is a major benefit of C4 carbon-concentrating mechanisms?", ["They reduce photorespiratory losses in many hot conditions", "They remove the need for ATP", "They prevent all water loss", "They eliminate the Calvin cycle"], "They reduce photorespiratory losses in many hot conditions", "Concentrating CO2 around RuBisCO suppresses its oxygenase activity."),
                ("Which molecules deliver energy and reducing power to carbon assimilation?", ["ATP and NADPH", "DNA and cellulose", "Oxygen and nitrogen", "Starch and chlorophyll"], "ATP and NADPH", "The Calvin–Benson cycle consumes ATP and NADPH."),
                ("Why distinguish gross from net photosynthesis?", ["Respiration affects the net carbon exchange", "Gross and net rates are always identical", "Net photosynthesis measures only sunlight", "Gross rate excludes carbon fixation"], "Respiration affects the net carbon exchange", "Net exchange reflects photosynthetic uptake minus respiratory release.")
            ],
            "challenge_questions": [
                ("Under hot, dry conditions, stomatal closure most directly reduces what?", ["Intercellular CO2 availability", "The wavelength of sunlight", "The number of chromosomes", "The plant's need for ATP"], "Intercellular CO2 availability", "Closing stomata conserves water but restricts CO2 diffusion."),
                ("Why can a higher O2-to-CO2 ratio increase photorespiration in C3 plants?", ["RuBisCO is more likely to oxygenate RuBP", "ATP synthase stops needing protons", "Chlorophyll begins fixing nitrogen", "The Calvin cycle moves into the nucleus"], "RuBisCO is more likely to oxygenate RuBP", "Higher relative oxygen availability favors RuBisCO's oxygenase reaction."),
                ("An experiment increases CO2 but shows no change in rate at saturating CO2. What is a reasonable inference?", ["Another constraint may dominate", "Carbon fixation has stopped existing", "The plant no longer uses light", "The measured rate must be false"], "Another constraint may dominate", "Light, temperature, or biochemical capacity may be limiting instead."),
                ("How does CAM timing help many plants in arid environments?", ["CO2 uptake can occur at night when water loss is lower", "All photosynthesis happens without light", "CAM plants do not use stomata", "It removes the need to store carbon"], "CO2 uptake can occur at night when water loss is lower", "Night-time stomatal opening can reduce transpiration in dry conditions."),
                ("Why should an experiment control both temperature and CO2 when testing light response?", ["They can independently affect the measured rate", "They are products of the light reaction", "They cannot affect enzymes", "They make replication unnecessary"], "They can independently affect the measured rate", "Multiple limiting factors can confound an observed light response.")
            ],
            "related": ["Photosystems and ATP synthase", "Photorespiration", "C3, C4, and CAM pathways"]
        }
    },
    "machine learning": {
        "Beginner": {
            "title": "Machine Learning: Learning from Examples",
            "explanation": "Machine learning is a way for computers to find patterns in examples and use those patterns to make predictions. Instead of writing every rule by hand, we give a model data to learn from. For example, a model can learn from labelled pictures of cats and dogs. The examples used to teach it are called training data. After training, we test the model on examples it has not seen. A model that memorizes training examples may perform poorly on new ones. This is why we care about generalization, or doing well on unfamiliar data. Good data and fair testing help us judge whether a model is useful.",
            "points": ["A dataset contains examples and their features. Features are the pieces of information a model uses to learn patterns.", "A model is the learned system that maps input features to a prediction. Different models can learn different kinds of relationships.", "Training adjusts model parameters using examples. The goal is to learn useful patterns rather than simply memorize each row.", "A test set checks performance on unseen examples. It should not be repeatedly used to tune every decision.", "Overfitting happens when a model fits training data too closely and struggles on new data. More representative data and simpler models can help."],
            "questions": [
                ("What is training data used for?", ["Teaching a model patterns", "Displaying app colours", "Charging the computer", "Replacing all testing"], "Teaching a model patterns", "Training examples are used to fit the model."),
                ("What is a feature?", ["An input property used for prediction", "The final grade only", "A computer's power cable", "A random file name"], "An input property used for prediction", "Features describe an example for the model."),
                ("Why test on unseen examples?", ["To estimate performance on new data", "To guarantee 100% accuracy", "To change labels automatically", "To avoid collecting data"], "To estimate performance on new data", "Unseen data gives a more realistic check of generalization."),
                ("What is a model's prediction?", ["Its output for an input", "The training file name", "A human-written rule only", "The number of rows in a spreadsheet"], "Its output for an input", "A model maps input information to an output."),
                ("What is overfitting?", ["Learning training details that do not generalize", "Never using training data", "Always predicting randomly", "Deleting all features"], "Learning training details that do not generalize", "An overfit model performs worse on unfamiliar examples.")
            ],
            "challenge_questions": [
                ("A model scores high on training data but low on test data. What is a likely issue?", ["Overfitting", "Perfect generalization", "No training occurred", "The test set trained itself"], "Overfitting", "The gap suggests the model has not generalized well."),
                ("Why should duplicate records be checked before splitting data?", ["Duplicates can leak across splits and inflate scores", "Duplicates always improve fairness", "Duplicates remove all labels", "Splitting requires identical rows"], "Duplicates can leak across splits and inflate scores", "Near-identical examples in train and test can make evaluation overly optimistic."),
                ("Which example is supervised learning?", ["Learning from examples paired with correct labels", "Grouping data without labels only", "Sorting files by size", "Compressing a folder"], "Learning from examples paired with correct labels", "Supervised training uses known target labels."),
                ("What should a test set represent?", ["Data similar to the intended real-world use", "Only the easiest training examples", "Only mislabeled records", "The model's source code"], "Data similar to the intended real-world use", "A representative test set better estimates real deployment performance."),
                ("What is the purpose of a baseline model?", ["Provide a simple comparison point", "Guarantee the final model wins", "Remove the need for evaluation", "Hide poor results"], "Provide a simple comparison point", "A baseline shows whether added complexity improves performance.")
            ],
            "related": ["Training and testing", "Classification and regression", "Overfitting"]
        },
        "Intermediate": {
            "title": "Machine Learning: Evaluation and Generalization",
            "explanation": "A machine-learning workflow defines a target, prepares features, splits data, trains a model, and evaluates generalization. Supervised learning uses labelled targets, while unsupervised learning looks for structure without a supplied target. Model parameters are learned from data, whereas hyperparameters control the learning procedure. A validation set or cross-validation helps compare model choices without using the final test set for tuning. Accuracy can be misleading when classes are imbalanced, so precision, recall, and F1 may be more informative. Data leakage occurs when information unavailable at prediction time enters training. Reliable evaluation therefore depends on both suitable metrics and careful experimental design.",
            "points": ["Supervised tasks include classification and regression, while clustering is a common unsupervised task. The target and goal determine the problem type.", "Parameters are learned during fitting; hyperparameters, such as tree depth, are selected through model development.", "Train, validation, and test data serve different roles. Keep the final test set untouched until model selection is complete.", "Precision measures how many predicted positives are correct, while recall measures how many actual positives are found. Their trade-off depends on the application.", "Leakage introduces information that would not legitimately be available at prediction time. It can make offline scores look much better than real performance."],
            "questions": [
                ("Which task predicts a continuous numeric target?", ["Regression", "Clustering", "Classification only", "Tokenization"], "Regression", "Regression models predict numeric quantities."),
                ("What is a hyperparameter?", ["A setting chosen outside the fitting of model parameters", "A test label", "A duplicate row", "Always the model's final prediction"], "A setting chosen outside the fitting of model parameters", "Hyperparameters configure the learning process."),
                ("What does recall measure for a positive class?", ["Fraction of actual positives found", "Fraction of predicted positives that are correct", "Overall number of features", "Training time per epoch"], "Fraction of actual positives found", "Recall is true positives divided by all actual positives."),
                ("Why keep a final test set untouched during tuning?", ["To avoid biased evaluation from repeated selection", "To make training slower", "To increase leakage", "To remove the target variable from training"], "To avoid biased evaluation from repeated selection", "Repeated test-guided decisions cause the test set to influence model selection."),
                ("What is data leakage?", ["Using information unavailable at prediction time", "Normalizing training features", "Splitting data randomly in all cases", "Reporting a confusion matrix"], "Using information unavailable at prediction time", "Leakage gives the model an unfair source of predictive information.")
            ],
            "challenge_questions": [
                ("In a rare-disease classifier, missing true cases is costly. Which metric deserves special attention?", ["Recall", "Training accuracy alone", "Number of columns", "File size"], "Recall", "Recall focuses on the proportion of actual positive cases detected."),
                ("A preprocessing scaler is fitted on all data before splitting. What is the concern?", ["Test-set information leaks into preprocessing", "The labels become text automatically", "The model cannot have parameters", "The dataset becomes unsupervised"], "Test-set information leaks into preprocessing", "Fit preprocessing on training data only, then apply it to held-out data."),
                ("Why can accuracy be misleading with a 99% negative class?", ["A model predicting negative every time can score 99%", "Accuracy ignores every correct prediction", "Accuracy always equals recall", "The positive class disappears"], "A model predicting negative every time can score 99%", "The majority class dominates the overall accuracy value."),
                ("When is cross-validation useful?", ["Comparing model choices across multiple data folds", "Guaranteeing no distribution shift", "Replacing the need for labels in supervised learning", "Making the test data part of training"], "Comparing model choices across multiple data folds", "Cross-validation estimates performance across different train-validation splits."),
                ("A feature is created using information recorded after the outcome. Why is it invalid?", ["It would not be available at prediction time", "It has too many rows", "It is necessarily categorical", "It guarantees underfitting"], "It would not be available at prediction time", "Post-outcome information leaks the answer into the features.")
            ],
            "related": ["Classification metrics", "Cross-validation", "Data leakage"]
        },
        "Advanced": {
            "title": "Machine Learning: Statistical Evaluation and Model Risk",
            "explanation": "Advanced model development treats performance as an estimate under a data-generating process, not as a single score. A defensible evaluation protocol separates model fitting, hyperparameter selection, and final assessment to limit selection bias. Cross-validation can estimate variability, but its validity depends on matching the split strategy to the data structure, such as time, group, or patient identity. Class imbalance, calibration, threshold selection, and asymmetric error costs affect which metric is operationally meaningful. Leakage can occur through features, preprocessing, target construction, or repeated test-set decisions. Distribution shift can also make a valid offline estimate unreliable after deployment. A strong workflow documents assumptions, uses appropriate baselines, and monitors performance after release.",
            "points": ["Evaluation estimates depend on the sampling process and independence assumptions. Grouped or temporal data often require structured splits rather than random row-level splitting.", "Nested cross-validation can separate hyperparameter selection from performance estimation when data is limited. The outer evaluation should not guide inner model choices.", "Calibration asks whether predicted probabilities match observed frequencies. Ranking quality and probability reliability are different properties.", "Thresholds should reflect the costs of false positives and false negatives. A default threshold is not automatically optimal for a real application.", "Distribution shift can change feature or target relationships after deployment. Monitoring and periodic reassessment are part of model reliability."],
            "questions": [
                ("Why use nested cross-validation for model comparison?", ["Separate tuning from performance estimation", "Guarantee identical folds for every dataset", "Remove all sampling uncertainty", "Eliminate the need for an evaluation metric"], "Separate tuning from performance estimation", "The outer loop estimates performance while the inner loop selects hyperparameters."),
                ("What does calibration evaluate?", ["Agreement between predicted probabilities and observed frequencies", "Only the ordering of examples", "The number of model parameters", "The speed of preprocessing"], "Agreement between predicted probabilities and observed frequencies", "A calibrated 0.8 probability group should have roughly 80% positive outcomes."),
                ("Why use group-aware splitting for repeated records per person?", ["Prevent related records crossing train and test", "Increase the number of labels", "Force class balance in every case", "Make features independent by definition"], "Prevent related records crossing train and test", "Related observations across splits can inflate estimated generalization."),
                ("What determines a useful classification threshold?", ["Error costs and deployment objectives", "Only the model's file size", "The order of feature names", "A universal fixed value for every task"], "Error costs and deployment objectives", "Threshold selection should reflect the costs and goals of the application."),
                ("What is distribution shift?", ["A change in the data distribution between development and deployment", "A change in Python indentation", "A guarantee of improved accuracy", "A method for sorting labels"], "A change in the data distribution between development and deployment", "Deployment data may differ from the data used to build or evaluate the model.")
            ],
            "challenge_questions": [
                ("A dataset contains multiple visits per patient. Which split best guards against patient leakage?", ["Group splits by patient", "Randomly split every visit row", "Put all visits in training and none in testing", "Sort by label then split adjacent rows"], "Group splits by patient", "All records from one patient should remain within one partition."),
                ("A model has strong AUC but poorly calibrated probabilities. What is true?", ["It may rank cases well while probability estimates remain unreliable", "Its probabilities must be correct", "Its recall must equal 1", "It cannot classify any cases"], "It may rank cases well while probability estimates remain unreliable", "AUC measures ranking and does not ensure calibrated probabilities."),
                ("Repeatedly selecting models based on the final test score primarily risks what?", ["Selection bias in the reported test performance", "Guaranteed reduction in variance", "Removing all overfitting", "Converting classification into clustering"], "Selection bias in the reported test performance", "Repeated test-set feedback indirectly fits decisions to the test set."),
                ("Why might a temporal split be needed for forecasting?", ["It preserves the direction of time and avoids future-to-past leakage", "It guarantees all classes are balanced", "It uses future labels to train earlier predictions", "It removes seasonality automatically"], "It preserves the direction of time and avoids future-to-past leakage", "Training on future information would not match the real forecasting setting."),
                ("A false negative is far more costly than a false positive. What should be reconsidered?", ["Decision threshold and recall-related trade-offs", "Only the colour of the dashboard", "The random seed alone", "The number of file extensions"], "Decision threshold and recall-related trade-offs", "Threshold choice should account for asymmetric error costs.")
            ],
            "related": ["Nested cross-validation", "Probability calibration", "Distribution shift and monitoring"]
        }
    }
}


def get_offline_lesson(topic, level):
    """Return a built-in lesson instantly, without requiring Ollama."""
    normalized = topic.strip().casefold()
    aliases = {
        "python": "python", "python basics": "python", "python fundamentals": "python",
        "photosynthesis": "photosynthesis", "machine learning": "machine learning",
        "ml": "machine learning"
    }
    key = aliases.get(normalized)
    if key is None:
        return None

    data = OFFLINE_LESSONS[key][level]

    def pack(rows):
        return [
            {"q": q, "options": options, "answer": answer, "why": why}
            for q, options, answer, why in rows
        ]

    return {
        "title": data["title"],
        "explanation": data["explanation"],
        "points": data["points"],
        "questions": pack(data["questions"]),
        "challenge_questions": pack(data["challenge_questions"]),
        "related": data["related"],
    }


# =========================================================

# 4. AI LESSON GENERATION

# =========================================================

def generate_ai_lesson(topic, level):

    """

    Generate level-specific explanations, key points,

    practice questions and separate challenge questions.

    No cache is used, so creating a lesson again generates

    fresh content for the selected level.

    """

    level_instructions = {

        "Beginner": """

        Teach a complete beginner.

        Define every important term in simple language.

        Use a familiar everyday analogy and a simple example.

        Explain the basic ideas step by step.

        Avoid unexplained technical jargon.

        Practice questions should test basic understanding.

        Challenge questions should be simple applications of the ideas.

        """,

        "Intermediate": """

        Assume the student knows the basic definitions.

        Explain how and why the concepts work.

        Discuss relationships between concepts and practical applications.

        Include a realistic worked example.

        Use appropriate technical terminology and explain it.

        Practice questions should test understanding and interpretation.

        Challenge questions should require applying concepts to new situations.

        """,

        "Advanced": """

        Teach at a technically advanced level.

        Explain mechanisms, assumptions, limitations and trade-offs.

        Include a complex practical scenario or technical example.

        Discuss edge cases and the reasoning behind design choices.

        Do not merely repeat introductory definitions.

        Practice questions should test technical understanding.

        Challenge questions should require multi-step reasoning,

        problem solving, or evaluation of complex scenarios.

        """

    }

    prompt = f"""

You are StudySpark, a careful and knowledgeable educational tutor.

TOPIC: {topic}

STUDENT LEVEL: {level}

TEACHING REQUIREMENTS FOR THIS LEVEL:

{level_instructions[level]}

Create a substantial and accurate learning lesson specifically for

this topic and level.

IMPORTANT:

The lesson must genuinely change with the selected level.

Do not produce the same generic explanation for all levels.

The five Spark points must be meaningful subtopics, not short headings.

Each Spark point must include a useful explanation of at least two sentences.

The explanation must be detailed, approximately 8 to 12 sentences.

Include an example appropriate for the selected level.

Return ONLY one valid JSON object with this exact structure:

{{

  "title": "A clear topic title",

  "explanation": "An 8 to 12 sentence explanation appropriate to the selected level.",

  "points": [

    "Subtopic 1: explain the idea in detail.",

    "Subtopic 2: explain the idea in detail.",

    "Subtopic 3: explain the idea in detail.",

    "Subtopic 4: explain the idea in detail.",

    "Subtopic 5: explain the idea in detail."

  ],

  "questions": [

    {{

      "q": "A practice question testing understanding.",

      "options": ["Option A", "Option B", "Option C", "Option D"],

      "answer": "Exact correct option",

      "why": "Explain the correct answer in 2 sentences."

    }}

  ],

  "challenge_questions": [

    {{

      "q": "A different, harder question requiring application or reasoning.",

      "options": ["Option A", "Option B", "Option C", "Option D"],

      "answer": "Exact correct option",

      "why": "Explain the reasoning in 2 sentences."

    }}

  ],

  "related": [

    "Related topic 1",

    "Related topic 2",

    "Related topic 3"

  ]

}}

STRICT RULES:

1. Return exactly 5 practice questions.

2. Return exactly 5 challenge questions.

3. All 10 questions must be different.

4. Practice questions must be easier than challenge questions.

5. Each question must have exactly 4 distinct options.

6. Each answer must exactly match one of its four options.

7. Every explanation must be accurate and relevant to the topic.

8. Do not use filler such as "learn more about the topic."

9. Do not use the same five generic points for unrelated topics.

10. Return valid JSON only. Do not use Markdown code fences.

"""

    response = requests.post(

        OLLAMA_URL,

        json={

            "model": OLLAMA_MODEL,

            "prompt": prompt,

            "stream": False,

            "format": "json",

            "options": {

                "temperature": 0.5,

                "num_predict": 3500,

            },

        },

        timeout=(2, 60),

    )

    response.raise_for_status()

    raw = response.json().get("response", "").strip()

    if not raw:

        raise ValueError("Ollama returned an empty response.")

    lesson = json.loads(raw)

    required = {

        "title",

        "explanation",

        "points",

        "questions",

        "challenge_questions",

        "related",

    }

    if not isinstance(lesson, dict) or not required.issubset(lesson):

        raise ValueError("The generated lesson is missing required fields.")

    if not isinstance(lesson["title"], str) or not lesson["title"].strip():

        raise ValueError("The lesson title is missing.")

    if not isinstance(lesson["explanation"], str):

        raise ValueError("The lesson explanation is invalid.")

    if len(lesson["explanation"].split()) < 50:

        raise ValueError(

            "The AI explanation was too short. Please create the lesson again."

        )

    if not isinstance(lesson["points"], list) or len(lesson["points"]) != 5:

        raise ValueError("The AI must generate exactly five Spark points.")

    for point in lesson["points"]:

        if not isinstance(point, str) or len(point.split()) < 8:

            raise ValueError(

                "One or more Spark points are too short. Please try again."

            )

    if not isinstance(lesson["related"], list) or len(lesson["related"]) < 3:

        raise ValueError("The AI must generate at least three related topics.")

    for field in ("questions", "challenge_questions"):

        questions = lesson[field]

        if not isinstance(questions, list) or len(questions) != 5:

            raise ValueError(

                f"The AI must generate exactly five {field.replace('_', ' ')}."

            )

        for question in questions:

            if not isinstance(question, dict):

                raise ValueError("An AI question has an invalid format.")

            if not all(

                key in question

                for key in ("q", "options", "answer", "why")

            ):

                raise ValueError("An AI question is missing required fields.")

            if not isinstance(question["options"], list):

                raise ValueError("Question options must be a list.")

            if len(question["options"]) != 4:

                raise ValueError("Every question must have four options.")

            if len(set(question["options"])) != 4:

                raise ValueError("Every question must have four distinct options.")

            if question["answer"] not in question["options"]:

                raise ValueError(

                    "A correct answer does not match the available options."

                )

            if not question["q"].strip() or not question["why"].strip():

                raise ValueError("A question or explanation is empty.")

    practice_text = {

        question["q"].strip().casefold()

        for question in lesson["questions"]

    }

    challenge_text = {

        question["q"].strip().casefold()

        for question in lesson["challenge_questions"]

    }

    if practice_text.intersection(challenge_text):

        raise ValueError(

            "Practice and Challenge contain duplicate questions. Try again."

        )

    return lesson

# =========================================================

# 5. SIDEBAR

# =========================================================

with st.sidebar:

    st.markdown("## 🪐 StudySpark")

    st.caption("YOUR PERSONAL LEARNING UNIVERSE")

    st.divider()

    st.markdown("### Mission controls")

    st.selectbox(

        "Choose your level",

        ["Beginner", "Intermediate", "Advanced"],

        key="selected_level",

    )

    st.radio(

        "Choose a mission",

        [

            "🔍 Understand",

            "🧩 Practice",

            "⚔️ Challenge",

            "🗺️ Explore",

        ],

        key="selected_mode",

    )

    st.divider()

    st.markdown("### Your journey")

    st.metric(

        "Missions completed",

        st.session_state.missions_completed,

    )

    st.metric(

        "Best quiz score",

        f"{st.session_state.best_score}%",

    )

    st.caption("Offline samples work without Ollama. AI generation is optional.")

# =========================================================

# 6. HEADER

# =========================================================

st.html(textwrap.dedent("""

<div class="hero">

    <div class="eyebrow">LEARN • EXPLORE • LEVEL UP</div>

    <h1>Your next big idea starts here.</h1>

    <p>Choose a topic. Pick a mission. Build your understanding one step at a time.</p>

</div>

"""))

c1, c2, c3 = st.columns(3)

with c1:

    st.html(textwrap.dedent("""

    <div class="metric">

        <div class="metric-number">🪐</div>

        <div>Learning universe</div>

        <div class="muted">Your space to explore</div>

    </div>

    """))

with c2:

    st.html(textwrap.dedent(f"""

    <div class="metric">

        <div class="metric-number">{st.session_state.missions_completed}</div>

        <div>Missions completed</div>

        <div class="muted">Every step counts</div>

    </div>

    """))

with c3:

    st.html(textwrap.dedent(f"""

    <div class="metric">

        <div class="metric-number">{st.session_state.best_score}%</div>

        <div>Personal best</div>

        <div class="muted">Quiz performance</div>

    </div>

    """))

# =========================================================

# 7. CREATE MISSION

# =========================================================

st.write("")

st.markdown("## Create a learning mission")

st.write(

    "Try **Python**, **Photosynthesis**, or **Machine Learning**, "

    "or enter any other topic."

)

with st.form("mission_form"):
    topic_input = st.text_input(
        "What would you like to learn?",
        placeholder="e.g. Python, Photosynthesis, Machine Learning",
        max_chars=100,
    )

    use_ollama = st.checkbox(
        "Use Ollama to generate a new AI lesson (optional; requires Ollama)",
        value=False,
        help="Leave unchecked to open built-in sample lessons instantly without Ollama.",
    )

    create_clicked = st.form_submit_button(
        "🚀 Create my mission",
        type="primary",
        use_container_width=True,
    )

if create_clicked:
    topic = topic_input.strip()
    selected_level = st.session_state.selected_level

    if not topic:
        st.warning("Enter a topic to begin your mission.")
    else:
        st.session_state.ai_error = ""
        new_lesson = None

        # The default path is instant and offline. Ollama is optional.
        if use_ollama:
            try:
                with st.spinner(
                    f"StudySpark is creating a {selected_level.lower()} lesson "
                    f"about {topic} with Ollama..."
                ):
                    new_lesson = generate_ai_lesson(topic, selected_level)
            except Exception as error:
                # If a built-in sample exists, keep the app useful when Ollama
                # is missing, stopped, or unable to generate valid JSON.
                new_lesson = get_offline_lesson(topic, selected_level)
                if new_lesson is not None:
                    st.info(
                        "Ollama was unavailable or could not create a valid lesson. "
                        "Loaded the built-in offline sample instead."
                    )
                else:
                    st.session_state.ai_error = (
                        f"AI lesson generation failed: {error}. "
                        "Try Python, Photosynthesis, or Machine Learning for an "
                        "offline sample, or check that Ollama is running."
                    )
        else:
            new_lesson = get_offline_lesson(topic, selected_level)
            if new_lesson is None:
                st.session_state.ai_error = (
                    f'"{topic}" does not have a built-in offline sample yet. '
                    "Choose Python, Photosynthesis, or Machine Learning, or enable "
                    "the optional Ollama AI generation checkbox."
                )

        if new_lesson is not None:
            st.session_state.lesson = new_lesson
            st.session_state.lesson_topic = topic
            st.session_state.lesson_level = selected_level
            st.session_state.quiz_submitted = False
            st.session_state.quiz_answers = {}
            st.session_state.quiz_score = 0
            st.session_state.quiz_percentage = 0
            st.session_state.quiz_attempt += 1
            st.session_state.practice_checked = {}
            st.session_state.mission_finished = False
            st.session_state.mission_id += 1
            st.session_state.reflection_saved = ""
            st.success(
                f"Your {selected_level.lower()} lesson is ready!"
            )
            st.rerun()

        if st.session_state.ai_error:
            st.error(st.session_state.ai_error)

# =========================================================

# 8. DISPLAY ACTIVE LESSON

# =========================================================

lesson = st.session_state.lesson

current_mode = st.session_state.selected_mode

# Errors are shown once in the mission-creation section above.
# Do not repeat the same error here on every Streamlit rerun.
if lesson:

    if st.session_state.lesson_level != st.session_state.selected_level:

        st.warning(

            f"This lesson was created for {st.session_state.lesson_level}. "

            f"You selected {st.session_state.selected_level}. "

            "Create the topic again to generate content for the new level."

        )

    st.divider()

    st.html(

        f"""

        <div style="background:white;border:1px solid #E9E8F4;

                    border-radius:18px;padding:24px;margin:12px 0;">

            <div style="color:#5145A5;font-weight:700;font-size:12px;

                        letter-spacing:1.4px;">

                ACTIVE LEARNING MISSION

            </div>

            <h2>🪐 {escape(str(lesson["title"]))}</h2>

            <p class="muted">

                Level: {escape(st.session_state.lesson_level)}

                &nbsp; • &nbsp;

                Mode: {escape(current_mode)}

            </p>

        </div>

        """

    )

    # -----------------------------------------------------

    # UNDERSTAND MODE

    # -----------------------------------------------------

    if "Understand" in current_mode:

        st.markdown("### 🔍 Core concept")

        st.html(

            f'<div class="lesson-explanation">'

            f'{escape(lesson["explanation"])}</div>'

        )

        st.markdown("### 💡 Spark points")

        for i, point in enumerate(lesson["points"], start=1):

            with st.container(border=True):

                st.markdown(f"**{i:02d} ✦**")

                st.write(point)

        st.markdown("### 🌍 Real-world connection")

        st.write(

            f"Think of one situation where **{st.session_state.lesson_topic}** "

            "could be useful. How would you explain it to another student?"

        )

        with st.expander("📝 Explain it in your own words"):

            reflection = st.text_area(

                "My explanation",

                placeholder="I understand this topic as...",

                key=f"reflection_{st.session_state.mission_id}",

            )

            if st.button("Save reflection"):

                if reflection.strip():

                    st.session_state.reflection_saved = reflection.strip()

                    st.success("Reflection saved for this session.")

                else:

                    st.warning("Write a few words first.")

            if st.session_state.reflection_saved:

                st.caption("Your saved reflection:")

                st.write(st.session_state.reflection_saved)

    # -----------------------------------------------------

    # PRACTICE MODE

    # -----------------------------------------------------

    elif "Practice" in current_mode:

        st.markdown("### 🧩 Practice zone")

        st.write(

            "These questions test your understanding. Type the exact "

            "answer shown among the options to check your response."

        )

        practice_questions = lesson["questions"]

        for i, question in enumerate(practice_questions):

            practice_key = f"{st.session_state.mission_id}_{i}"

            with st.container(border=True):

                st.markdown(f"**Question {i + 1}. {question['q']}**")

                user_answer = st.text_input(

                    "Your answer",

                    key=f"practice_input_{practice_key}",

                    placeholder="Type your answer...",

                )

                if st.button(

                    "Check Answer",

                    key=f"check_practice_{practice_key}",

                    type="primary",

                ):

                    if user_answer.strip():

                        st.session_state.practice_checked[practice_key] = True

                    else:

                        st.warning("Write your answer before checking.")

                if st.session_state.practice_checked.get(

                    practice_key, False

                ):

                    expected = question["answer"].strip().casefold()

                    actual = user_answer.strip().casefold()

                    if actual == expected:

                        st.success("Correct! Well done.")

                    else:

                        st.info("Good attempt! Review the suggested answer.")

                    st.markdown("**Correct answer:**")

                    st.write(question["answer"])

                    st.caption(question["why"])

    # -----------------------------------------------------

    # CHALLENGE MODE — SEPARATE QUESTIONS

    # -----------------------------------------------------

    elif "Challenge" in current_mode:

        st.markdown("### ⚔️ Challenge arena")

        st.write(

            "These are separate, harder questions designed to test "

            "application and reasoning."

        )

        challenge_questions = lesson["challenge_questions"]

        form_key = (

            f"challenge_form_{st.session_state.mission_id}_"

            f"{st.session_state.quiz_attempt}"

        )

        with st.form(form_key):

            answers = {}

            for i, question in enumerate(challenge_questions):

                st.markdown(

                    f"**Question {i + 1} of {len(challenge_questions)}**"

                )

                st.write(question["q"])

                answers[i] = st.radio(

                    "Select one answer",

                    question["options"],

                    key=(

                        f"challenge_{st.session_state.mission_id}_"

                        f"{st.session_state.quiz_attempt}_{i}"

                    ),

                    index=None,

                )

            quiz_submit = st.form_submit_button(

                "🏁 Submit challenge",

                type="primary",

                use_container_width=True,

            )

        if quiz_submit:

            score = sum(

                1

                for i, question in enumerate(challenge_questions)

                if answers.get(i) == question["answer"]

            )

            total = len(challenge_questions)

            percentage = round(score / total * 100) if total else 0

            st.session_state.quiz_answers = answers

            st.session_state.quiz_submitted = True

            st.session_state.quiz_score = score

            st.session_state.quiz_percentage = percentage

            st.session_state.best_score = max(

                st.session_state.best_score,

                percentage,

            )

            st.rerun()

        if st.session_state.quiz_submitted:

            score = st.session_state.quiz_score

            percentage = st.session_state.quiz_percentage

            total = len(challenge_questions)

            st.divider()

            st.markdown("### 🏆 Mission results")

            st.progress(percentage / 100)

            st.subheader(f"You scored {score}/{total} — {percentage}%")

            if percentage == 100:

                st.balloons()

                st.success("Outstanding! You mastered this challenge.")

            elif percentage >= 50:

                st.info("Good progress! Review the explanations below.")

            else:

                st.warning(

                    "Keep practising. Review the answers and try again."

                )

            for i, question in enumerate(challenge_questions):

                chosen = st.session_state.quiz_answers.get(i)

                correct = chosen == question["answer"]

                with st.container(border=True):

                    st.markdown(f"**{i + 1}. {question['q']}**")

                    st.write(

                        f"Your answer: {chosen or 'No answer selected'}"

                    )

                    if correct:

                        st.success("Correct!")

                    else:

                        st.error(

                            f"Correct answer: {question['answer']}"

                        )

                    st.caption(question["why"])

            if st.button("🔄 Try the challenge again"):

                st.session_state.quiz_submitted = False

                st.session_state.quiz_answers = {}

                st.session_state.quiz_attempt += 1

                st.rerun()

    # -----------------------------------------------------

    # EXPLORE MODE

    # -----------------------------------------------------

    elif "Explore" in current_mode:

        st.markdown("### 🗺️ Knowledge map")

        st.write("Explore the topic through these learning paths.")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("#### 🔑 Start here")

            st.write(lesson["explanation"])

            st.markdown("#### 💡 Key concepts")

            for point in lesson["points"]:

                st.write(f"• {point}")

        with col2:

            st.markdown("#### 🌌 Explore next")

            for i, related in enumerate(lesson["related"], start=1):

                with st.container(border=True):

                    st.markdown(f"**{i}. {related}**")

            st.markdown("#### Check your understanding")

            st.write(

                "Switch to Challenge mode to test your understanding "

                "with the harder question set."

            )

    # -----------------------------------------------------

    # FINISH MISSION

    # -----------------------------------------------------

    st.divider()

    if not st.session_state.mission_finished:

        if st.button("✨ Finish this mission", type="primary"):

            st.session_state.mission_finished = True

            st.session_state.missions_completed += 1

            st.rerun()

    else:

        st.success("Mission completed! Keep up the learning streak. 🎉")

# =========================================================

# 9. FOOTER

# =========================================================

st.write("")

st.html(textwrap.dedent("""

<div style="text-align:center;padding:24px;color:#77778E;">

    🪐 <b>StudySpark</b><br>

    Small steps. Big discoveries.<br>

    <span style="font-size:12px;">

        Hackathon prototype • Offline samples + optional Ollama AI

    </span>

</div>

"""))

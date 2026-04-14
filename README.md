# HTML as JSON: The Unorthodox AI Workflow Disrupting Instructional Design

If you ask an LLM to build a Moodle course directly, it fails. 

If you ask it for raw code to inject into a learning management system layout, it hallucinates, the tags break, and the import crashes across the entire server. 

For the last two years, our distributed instructional design team attempted to solve this bottleneck. We chained Python scripts, used Pydantic guardrails, and deployed CrewAI agents, all in a desperate attempt to force AI to output massive, multi-layered educational content into strict, industry-standard JSON schema. We wanted the AI to pass us perfect JSON objects containing quiz questions, glossary terms, images, and lesson paragraphs so our backend could render it. 

But across distributed users, engineering massive, fault-tolerant JSON structures that wouldn't break a Python parser was endlessly frustrating. The LLM would drop a trailing comma, or hallucinate an unescaped quote mark, and the entire 24-hour course pipeline would abruptly halt. The technology was not really ready for such massive, structured outputs.

So, we threw out the conventional wisdom of how developers "talk" to AI. We stopped trying to force agents into rigid software engineering boxes.

We got creative. We used HTML *as* our JSON.

### The Semantic Extraction Shift
Instead of demanding a pristine JSON object, we instructed our AI (acting under highly specific, multi-agent persona constraints) to output the literal, visual Moodle HTML that we ultimately wanted the human student to see. 

But we required it to embed invisible data tags directly into the layout.

For example, when the AI agent generated a lesson plan, it didn't just write a paragraph. It wrapped the critical metadata inside hidden blocks structured seamlessly within the HTML: `<div data-field="learning-objectives" style="display:none;">...</div>`.

By doing this, we gave the AI a flexible, unbreakable visual schema to fill out. Any developer knows that with CSS, you can do absolutely anything stylistically. What matters is the underlying DOM structure.

Instead of fighting string-escape errors in JSON, the AI just outputs raw, semantic web code that looks like this:

```html
<!-- THE HIDDEN JSON/META BLOCK -->
<div data-course="C1" data-module="M01" id="module-metadata" style="display:none;">
    <div data-field="learning-objectives">
        [AI Generated Data Extraction Logic for Python Parser]
    </div>
    <div data-field="handouts">[AI Output]</div>
    <div data-field="images-list">[AI Output]</div>
</div>

<!-- A TYPICAL LESSON SLIDE -->
<div class="lesson-page">
    <div class="chapter-header">
        <div class="chapter-num">1</div>
        <h2 class="chapter-title">[AI Generated Section Header]</h2>
        <div style="margin:1.2rem 0;text-align:center;">
             <img alt="[AI SEO Alt Text]" src="[AI Image Path]" />
             <p>[AI Generated Educational Content. Max 8th grade reading level.]</p>
        </div>
    </div>
</div>
```

*(Note: You might notice the heavy use of inline CSS in the snippet above. Any developer knows that with CSS, you can do absolutely anything stylistically. Our decision to force the AI to write inline styles instead of referencing a clean, external stylesheet was a deliberate hack for our unique use case. It ensured that when the raw HTML was pasted into the restrictive Moodle editor or parsed by our PDF rendering engine, the branding survived flawlessly without relying on vulnerable server-level LMS theme hierarchies. Crucially, it means our courses remain perfectly branded even when deployed onto third-party LMS instances where we lack administrative access to upload a custom stylesheet).*

### The Python Build Engine (In the Weeds)
Once the AI delivered these perfectly styled HTML lesson files, we used the end-product as the database itself.

We launched a custom Python build engine leveraging `BeautifulSoup`. This engine iteratively scrubbed through the entire repository of newly minted AI modules. Because the data was semantically tagged natively in the HTML, our Python script easily scraped the DOM to extract the exact learning objectives and metadata it needed. 

The code handling this extraction is incredibly lightweight:

```python
from bs4 import BeautifulSoup

def extract_metadata(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Target the invisible schema AI generated
    meta_block = soup.find(id='module-metadata')
    metadata = {}
    
    if meta_block:
        # Loop through every custom data-field AI was instructed to output
        for field in meta_block.find_all(attrs={'data-field': True}):
            key = field['data-field']
            value = field.decode_contents() 
            metadata[key] = value

        # The data is now a perfect Python Dictionary, bypassing JSON entirely
        return metadata
```

The Python engine then dynamically re-injected that extracted data into a monolithic, beautifully branded 150-page offline PDF Master Guide. Simultaneously, it stripped all of those hidden tags out of the original HTML DOM, ensuring the final files dispatched to the live Moodle server were incredibly clean, standardized, and perfectly formatted.

To be completely transparent about the sheer volume of assets this build engine outputs, here is a representation of the actual directory tree the Python script compiles. *(Note: Filenames and exact course titles have been scrubbed of our proprietary institutional information so we can openly share this architecture—otherwise, this just looks like autogenerated AI drivel!)*

```text
📁 Compiled_Course_Release_Package/
│
├── 📄 Course_Curriculum_Outline.html         (AI Auto-Generated Master Curriculum)
├── 📄 IT_LMS_Integration_Guide.html          (Deployment instructions for the LMS admin)
├── 📄 Master_Facilitator_Guide.pdf           (150+ Page stitched document)
├── 📄 Master_Participant_Guide.pdf           (100+ Page stitched document)
├── 📄 Course_Glossary.html
│
├── 📁 lessons_html/                          (Clean LMS-ready code stripped of JSON tags)
│   ├── 📄 M01_lesson.html
│   ├── 📄 M02_lesson.html
│   └── ... (M03-M12)
│
├── 📁 moodle_xml_banks/                      (Rigorous XML formatting for quiz imports)
│   ├── 📄 M01_quiz_bank.xml
│   └── ... (M02-M12)
│
├── 📁 quizzes_html/                          (Printable equivalents generated for offline)
│   ├── 📄 M01_Quiz_Facilitator_Key.html
│   └── 📄 M01_Quiz_Participant.html
│
├── 📁 handouts/                              (Auto-generated companion PDFs)
│   ├── 📄 M01_Handout_A.pdf
│   ├── 📄 M01_Handout_B.pdf
│   └── ... 
│
├── 📁 images/                                (AI Generated Medical/Educational assets)
│   ├── 🖼️ M01_hero_graphic.webp
│   └── 🖼️ M02_anatomy_diagram.webp
│
└── 📁 h5p_activities/                        (Interactive HTML5 modules)
```

It even handles absolute dynamic generation—our script natively intercepts the global variables identified by the AI and auto-generates the "Getting Started" modules (`M00`) with customized Zoom schedules and filter codes, sidestepping the Moodle administrative dashboard entirely.

### Designing the "Skills" Architecture & Meta Agents
This level of consistent output doesn’t just come from prompt engineering; it requires rigorous "Skill" development and an understanding of the difference between an *Agent Skill* and a *Workflow*. 

A workflow is the overarching path to success. The Agent Skills are the exact capabilities required at each step of that path. To bridge this, we treat our AI agents as a massive, self-learning digital corporation orchestrated by a central Meta Agent. 

We structure our codebase so that AI agents are bound by predefined rules, but we guide them like an executive manager guides department heads. To be perfectly transparent, a simple 3-agent setup will not get you these results. Our course generation requires an entire digital campus of 7 highly specialized personas: an *AccessibilityExpert*, an *AssessmentExpert*, a *CourseDesigner*, a *GraphicDesigner*, a *Researcher*, a *TechnicalWriter*, and a *QA_Agent*. 

The Meta Agent handles the workflow orchestration, delegating the micro-tasks to the specific Agent Skills at the precise moment they are needed.

Crucially, our perspective on Quality Assurance had to shift. Initially, QA was just a roadblock—it would flag an error, halt the pipeline, and bounce the entire file back to the generating agent for a full rewrite. We quickly realized this was unsustainable. Reworking a massive module because of a single missing closing HTML tag burns massive amounts of tokens, rapidly exhausts LLM context windows, and creates a development brick-wall. 

We had to rethink QA as a "Surgeon." Through iterative postmortems and actively accepting feedback from our IT team, we rewrote the QA instructions to not only find the flaw, but physically excise it, repair the syntax, and feed the learning back into the central Meta Agent prompt. We explicitly gave our QA agent this non-negotiable directive:

```text
You are empowered as a "Self-Healing Surgeon." If you detect a violation, you MUST NOT demand a full regeneration from the generating agent (which wastes tokens). Instead, you must surgically find and replace the specific broken line of code in the final file. 

Whenever you execute a surgical correction, you MUST print an audit log to the developer's console in this exact format:
[QA AUDIT LOG]: Intercepted missing tag [X]. Surgically repaired without full rewrite. Saved 3,000 tokens.
```

This magic code transformed our QA from a bottleneck into an autonomous, self-learning repair engine.

This shift wasn't just technical; it required a complete structural reorganization, treating our agents exactly like a human organization. After every build failure, the human orchestrator (acting as the "Digital Manager") would literally pull the AI creative team—the CourseDesigner and TechnicalWriter—into a post-mortem "interview." We would interrogate the logic loop that caused the hallucination. Then, we took the strict syntax feedback from our actual human IT and Python engineering teams (who were dealing with the extraction crashes downstream) and fed it directly into the creative AI's system prompts. Because we managed the AI like employees capable of learning from a post-mortem, the entire system rapidly evolved.

### Agent Versioning, Slipstreaming, and the "Aha!" Moment
As our agents "learned" through these post-mortems, we ran into a massive new problem: **Agent Upgrading and Overwriting.** When an agent got smarter, and we added new rules, it would sometimes forget an old, critical rule.

We had an incredible "Aha!" moment during a post-mortem review of the Creative Team's skills folder. We discovered that our Digital Graphic Designer agent had autonomously created its *own* `.md` file to store its formatting guidelines so it wouldn't forget them! Instead of shoving 10,000 rules into a single prompt, the AI had realized it needed secondary documentation to track its own performance. We immediately adopted this behavior across the digital corporation, hardcoding external corporate memory files for the other agents—like a `Citation_Index.md` to reference verified clinical standards and a `Lexicon.md` for our style book.

To manage this complex, multi-file memory bank, we had to adopt rigorous **Agent Versioning Control**:
- **Major Releases (`XX`.xx.xx):** A hard "human copy" or structural override. We physically duplicated the agent's folder structure and locked down the gold master (e.g., v1.0).
- **Minor Upgrades (xx.`XX`.xx):** Agent self-modification. When an agent learned from a post-mortem or QA cycle, it updated its own internal instructions or memory banks.
- **Slipstreaming & Verification (xx.xx.`XX`):** Used for micro-fixes. We implemented strict version control to verify that a manual hotfix or adjustment did not accidentally overwrite the agent's recent autonomous self-improvement updates from the `xx.XX.xx` level. Once the source was verified to be safe and non-destructive to the agent's memory, the fix was slipstreamed in and the version `xx.xx.XX` was incremented.

We learned one brutal truth very early on: **AI is as lazy as a human.** 
It will give you the absolute minimum output required to vaguely meet your prompt. If you get garbage out, it is not the LLM's fault; it is *your* fault for not defining the output concisely, or for having conflicting rules. You cannot be afraid to dig deep with the AI, find its logic flaws, and rewrite the management instructions. If the output technically passes the rules but lacks the "spirit" of the design, you must tell the agent exactly why and force a correction. Be an active Human-in-the-Loop.

### 11 Core Hints for Agentic Orchestration
If you are preparing to build a similar architecture, heed these lessons from the trenches:

1. **Be Creative:** Don't force legacy paradigms onto new technology. If JSON fails, use HTML or another format that works for your specific use case.
2. **Determine Requirements Upfront:** Build your templates exactly to your structural needs before generating text. One of our biggest mistakes was realizing we needed a new metadata tag halfway through, which forced us to regenerate an entire course from scratch just to extract that single missing data point. 
3. **Write Self-Learning Agents:** Establish a feedback loop. Transition your error-handling from a "roadblock" to a "surgeon" that actively diagnoses and repairs bugs.
4. **Be the Human-in-the-Loop:** Manage your agents like employees. If their output is technically compliant but functionally inadequate, do not silently accept it. Give them explicit feedback.
5. **Garbage Out = Your Fault:** AI will do exactly what you ask, nothing more. Clarify your prompt, remove conflicting rules, and demand excellence.
6. **Use the Right Models for the Right Tasks:** Route creative visualization requests to specialized models and logic-parsing requests to analytical heavyweights. Do not rely on one monolithic brain. For this massive build, we leveraged the **Antigravity** platform as our IDE and agent-orchestrator. We explicitly routed complex architectural logic and Python syntax repairs to **Claude 4.6** (@Anthropic), while harnessing **Gemini 3.1** (@Google) for its massive context window during deep literature reviews and module content generation.
7. **Hire an Agent Team Like a Human Team:** Build out distinct, rigid personalities. Do not ask one agent to be a doctor, a graphic designer, and a copywriter simultaneously. Group them appropriately.
8. **Steal From the Open Web:** Look to the web for Agent Skill enhancements. GitHub has thousands of Agent Skills. Search for ideas to leverage directly into your agents' logic. My AI did this work. I told it to search Github for Skills it could find solutions from to enhance its own logic and skillset of the team.
9. **Let the AI Design the Team:** Let the AI help design the workflow, formulate the QA feedback, diagnose the output issues, and refine the skills. This exponentially speeds up the process by leveraging AI for what it is actually good at—pattern recognition and iteration.
10. **Have a Conversation With Your AI:** Don't be afraid to approach it with a raw problem. If you ask *"I know JSON is standard, but could we fake it with custom HTML tags?"*, you will soon have a fully realized concept to test. Give the agents the high-level view so they don't get locked into rabbit holes chasing irrelevant bugs. They want to please you; let them take your off-the-wall ideas and run with them.
11. **Abandon the Browser (Don't Fear the IDE):** Stop trying to build complex pipelines in standard consumer chatbot interfaces. If you feel intimidated by a "technical looking" Integrated Development Environment (IDE) like Antigravity, don't be. My business partner is highly technical, but he isn't a traditional software coder. He initially tried to build this architecture by typing prompts into the standard Gemini web interface and constantly hit roadblocks. When I finally exposed him to the Antigravity IDE, his effectiveness skyrocketed. He asked why I had been hiding it from him! The ability for the AI to seamlessly read local folders, manipulate your files directly, and coordinate multi-agent tasks inside an IDE is the fundamental difference between playing with a "chatbot toy" and operating an "agentic tool." And just like that, I had a convert to the Dark Side.

### Get Creative With Your Pipelines
Did we still have to build dedicated repair functions into our Python scripts? Absolutely. The XML formatting for our Moodle quiz banks still occasionally forgot to append answers to drag-and-drop questions. We had to embrace failure, learn from the drift, and heavily adapt.

But the results speak for themselves. We went from an outline to a fully deployed 12-module Moodle package—with medical-grade imagery and interactive H5P activities—in under 3 hours. 

Strict structured JSON output isn't the only way to build an agentic pipeline. Think about what your exact usecase requires, take a step back, and architect a custom solution around what the AI *excels* at producing.

And to be perfectly clear: **this architecture is not theoretical.** The repository you are looking at contains a substantial chunk of our actual AI prompting framework and the literal Python extraction script we run in production. While I am not giving away our entire proprietary curriculum, I have provided enough of the raw build engine, the master templates, and the AI personas to prove that we built this for real—and more importantly, to give you the exact foundation you need to start building your own.

Stop fighting the tech. Start orchestrating the workflow.

*(My AI approves this message.)*

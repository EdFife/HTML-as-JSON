<div align="center">

# 🤖 HTML as JSON
### The Unorthodox AI Workflow Disrupting Instructional Design

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Build Engine](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Data Structure](https://img.shields.io/badge/HTML5-Semantic%20Web-orange.svg)](#)
[![AI Orchestration](https://img.shields.io/badge/Agents-Orchestrated-success.svg)](#)

</div>

---

If you ask an LLM to build a Moodle course directly, it fails. 

If you ask it for raw code to inject into a learning management system layout, it hallucinates, the tags break, and the import crashes across the entire server. 

For the last two years, our distributed instructional design team attempted to solve this bottleneck. We chained Python scripts, utilized OpenAI's Structured Outputs, tested MS AutoGen, enforced Pydantic guardrails, and deployed CrewAI agents, all in a desperate attempt to force AI to output massive, multi-layered educational content into strict, industry-standard JSON schema. We wanted the AI to pass us perfect JSON objects containing quiz questions, glossary terms, images, and lesson paragraphs so our backend could render it. 

But across distributed users, engineering massive, fault-tolerant JSON structures that wouldn't break a Python parser was endlessly frustrating. The LLM would drop a trailing comma, or hallucinate an unescaped quote mark, and the entire 24-hour course pipeline would abruptly halt. The technology was not really ready for such massive, structured outputs.

So, we threw out the conventional wisdom of how developers "talk" to AI. We stopped trying to force agents into rigid software engineering boxes.

We got creative. **We used HTML *as* our JSON.**

---

## 🏗️ The Semantic Extraction Shift

Instead of demanding a pristine JSON object, we instructed our AI (acting under highly specific, multi-agent persona constraints) to output the literal, visual Moodle HTML that we ultimately wanted the human student to see. 

But we required it to embed invisible data tags directly into the layout.

For example, when the AI agent generated a lesson plan, it didn't just write a paragraph. It wrapped the critical metadata inside hidden blocks structured seamlessly within the HTML: `<div data-field="learning-objectives" style="display:none;">...</div>`.

By doing this, we gave the AI a flexible, unbreakable visual schema to fill out. Any developer knows that with CSS, you can do absolutely anything stylistically. What matters is the underlying DOM structure.

Instead of fighting string-escape errors in JSON, the AI just outputs this raw, semantic web code directly:

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

> [!NOTE]  
> **Why Inline CSS?** You might notice the heavy use of inline CSS in the snippet above. Our decision to force the AI to write inline styles instead of referencing a clean, external stylesheet was a deliberate hack for our unique use case. It ensured that when the raw HTML was pasted into the restrictive Moodle editor or parsed by our PDF rendering engine, the branding survived flawlessly without relying on vulnerable server-level LMS theme hierarchies. Crucially, it means our courses remain perfectly branded even when deployed onto third-party LMS instances where we lack administrative access.

<br>

> [!TIP]  
> **Skipping the Translation Layer (Visual First vs. Data First)**
> 
> The typical industry workflow prioritizes the database over the human. The process usually looks like this:
> 1. AI generates strict JSON.
> 2. The Database ingests the JSON.
> 3. A web developer writes frontend templating logic to translate that JSON into a visual HTML layout.
>
> Our methodology eliminates Step 3. Instead of asking the AI to give us the blueprints so we can build the house, we instruct the AI to hand us the fully-built visual layout directly. It then stealthily uses invisible `data-*` attributes to "hang" the metadata on the back of the HTML elements, allowing our Python script to scan it like barcodes later. 

---

## ⚙️ The Python Build Engine

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

The Python engine then dynamically re-injected that extracted data into a monolithic, beautifully branded 150-page offline PDF Master Guide. Simultaneously, it stripped all of those hidden tags out of the original HTML DOM. After all, if we deployed the raw files to the live server, any clever student could simply right-click "View Page Source" and scrape all the hidden metadata tags. Stripping them out just makes the page source much less interesting.

> [!IMPORTANT]  
> To be completely transparent about the sheer volume of assets this build engine outputs, here is a representation of the actual directory tree the Python script compiles. *(Note: Filenames and exact course titles have been scrubbed of our proprietary institutional information so we can openly share this architecture—otherwise, this just looks like autogenerated AI drivel!)*

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
│   └── ... (M02-M12)
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
│   └── ... 
│
├── 📁 images/                                (AI Generated Medical/Educational assets)
│   ├── 🖼️ M01_hero_graphic.webp
│   └── 🖼️ M02_anatomy_diagram.webp
│
└── 📁 h5p_activities/                        (Interactive HTML5 modules)
```

It even handles absolute dynamic generation—our script natively intercepts the global variables identified by the AI and auto-generates the "Getting Started" modules (`M00`) with customized Zoom schedules and filter codes, sidestepping the Moodle administrative dashboard entirely.

---

## 👥 Designing the "Skills" Architecture & Meta Agents

This level of consistent output doesn’t just come from prompt engineering; it requires rigorous "Skill" development and an understanding of the difference between an *Agent Skill* and a *Workflow*. 

A workflow is the overarching path to success. The Agent Skills are the exact capabilities required at each step of that path. To bridge this, we treat our AI agents as a massive, self-learning digital corporation orchestrated by a central Meta Agent. 

We structure our codebase so that AI agents are bound by predefined rules, but we guide them like an executive manager guides department heads. To be perfectly transparent, a simple 3-agent setup will not get you these results. Our course generation requires an entire digital campus of 7 highly specialized personas: 

*   🧑‍🦯 *AccessibilityExpert*
*   📊 *AssessmentExpert*
*   🎓 *CourseDesigner*
*   🎨 *GraphicDesigner*
*   🔍 *Researcher*
*   📝 *TechnicalWriter*
*   🛠️ *QA_Agent* 

The Meta Agent handles the workflow orchestration, delegating the micro-tasks to the specific Agent Skills at the precise moment they are needed.

### The "Self-Healing Surgeon" QA Shift
Crucially, our perspective on Quality Assurance had to shift. Initially, QA was just a roadblock—it would flag an error, halt the pipeline, and bounce the entire file back to the generating agent for a full rewrite. We quickly realized this was unsustainable. Reworking a massive module because of a single missing closing HTML tag burns massive amounts of tokens, as well as degrading the quality of the content and rapidly exhausts LLM context windows, and creates a development brick-wall. 

We had to rethink QA as a "Surgeon." Through iterative postmortems and actively accepting feedback from our IT team, we rewrote the QA instructions to not only find the flaw, but physically excise it, repair the syntax, and feed the learning back into the central Meta Agent prompt. We explicitly gave our QA agent this non-negotiable directive:

```text
You are empowered as a "Self-Healing Surgeon." If you detect a violation, you MUST NOT demand a full regeneration from the generating agent (which wastes tokens). Instead, you must surgically find and replace the specific broken line of code in the final file. 

Whenever you execute a surgical correction, you MUST print an audit log to the developer's console in this exact format:
[QA AUDIT LOG]: Intercepted missing tag [X]. Surgically repaired without full rewrite. Saved 3,000 tokens.
```

This magic code transformed our QA from a bottleneck into an autonomous, self-learning repair engine.

This shift wasn't just technical; it required a complete structural reorganization, treating our agents exactly like a human organization. After every build failure, the human orchestrator (acting as the "Digital Manager") would literally pull the AI creative team—the CourseDesigner and TechnicalWriter—into a post-mortem "interview." We would interrogate the logic loop that caused the hallucination. Then, we took the strict syntax feedback from our actual human IT and Python engineering teams (who were dealing with the extraction crashes downstream) and fed it directly into the creative AI's system prompts. Because we managed the AI like employees capable of learning from a post-mortem, the entire system rapidly evolved.

---

## 🧠 Agent Versioning, Slipstreaming, and the "Aha!" Moment

As our agents "learned" through these post-mortems, we ran into a massive new problem: **Agent Upgrading and Overwriting.** When an agent got smarter, and we added new rules, it would sometimes forget an old, critical rule.

We had an incredible "Aha!" moment during a post-mortem review of the Creative Team's skills folder. We discovered that our Digital Graphic Designer agent had autonomously created its *own* `.md` file to store its formatting guidelines so it wouldn't forget them! Instead of shoving 10,000 rules into a single prompt, the AI had realized it needed secondary documentation to track its own performance. We immediately adopted this behavior across the digital corporation, hardcoding external corporate memory files for the other agents—like a `Citation_Index.md` to reference verified clinical standards and a `Lexicon.md` for our style book.

To manage this complex, multi-file memory bank, we had to adopt rigorous **Agent Versioning Control**:

- **[Major Releases] `XX.xx.xx`**: A hard "human copy" or structural override. We physically duplicated the agent's folder structure and locked down the gold master (e.g., v1.0).
- **[Minor Upgrades] `xx.XX.xx`**: Agent self-modification. When an agent learned from a post-mortem or QA cycle, it updated its own internal instructions or memory banks.
- **[Slipstreaming] `xx.xx.XX`**: Used for micro-fixes. We implemented strict version control to verify that a manual hotfix or adjustment did not accidentally overwrite the agent's recent autonomous self-improvement updates. Once verified safe, the fix was slipstreamed in.

> [!WARNING]  
> **The Brutal Truth:** AI is as lazy as a human. It will give you the absolute minimum output required to vaguely meet your prompt. If you get garbage out, it is not the LLM's fault; it is *your* fault for not defining the output concisely, or for having conflicting rules. You cannot be afraid to dig deep with the AI, find its logic flaws, and rewrite the management instructions. If the output technically passes the rules but lacks the "spirit" of the design, you must tell the agent exactly why and force a correction. Be an active Human-in-the-Loop.

---

## 🏆 10++ Core Hints for Agentic Orchestration

If you are preparing to build a similar architecture, heed these lessons from the trenches:

1. 🚀 **Be Creative:** Don't force legacy paradigms onto new technology. If JSON fails, use HTML or another format that works for your specific use case.
2. 🎯 **Determine Requirements Upfront:** Build your templates exactly to your structural needs before generating text. Finding a missing metadata tag halfway through forces massive regenerations.
3. 🩺 **Write Self-Learning Agents:** Establish a feedback loop. Transition your error-handling from a "roadblock" to a "surgeon" that actively diagnoses and repairs bugs.
4. 👨‍💻 **Be the Human-in-the-Loop:** Manage your agents like employees. If their output is technically compliant but functionally inadequate, do not silently accept it.
5. 🗑️ **Garbage Out = Your Fault:** AI will do exactly what you ask, nothing more. Clarify your prompt, remove conflicting rules, and demand excellence.
6. 🧠 **Use the Right Models for the Right Tasks:** Route creative requests to specialized models and logic-parsing requests to analytical heavyweights. For this build, we routed complex syntax repairs to **Claude 4.6 Sonnet** and **Claude 4.6 Opus** (via the Antigravity IDE), while harnessing **Gemini 3.1 Pro** for deep literature generation.
7. 🎭 **Hire an Agent Team Like a Human Team:** Build out distinct, rigid personalities. Group them appropriately instead of demanding one monolithic agent do everything.
8. 🌐 **Steal From the Open Web:** Search GitHub for Agent Skills to leverage directly into your agents' logic. Let your AI scan for solutions to enhance its own team.
9. 🤖 **Let the AI Design the Team:** Let the AI help design the workflow, formulate the QA feedback, and refine the skills via pattern recognition.
10. 💬 **Have a Conversation With Your AI:** Don't be afraid to approach it with a raw problem. If you ask *"I know JSON is standard, but could we fake it with custom HTML tags?"*, you will soon have a fully realized concept to test.
11. 🪄 **Abandon the Browser (Don't Fear the IDE):** Stop trying to build complex pipelines in standard consumer chatbot interfaces. If you feel intimidated by a "technical looking" Integrated Development Environment (IDE) like Antigravity, don't be. My business partner is highly technical, but he isn't a traditional software coder. He initially tried to build this architecture by typing prompts into the standard Gemini web interface and constantly hit roadblocks. When I finally exposed him to the Antigravity IDE, his effectiveness skyrocketed. He asked why I had been hiding it from him! The ability for the AI to seamlessly read local folders, manipulate your files directly, and coordinate multi-agent tasks inside an IDE is the fundamental difference between playing with a "chatbot toy" and operating an "agentic tool." And just like that, I had a convert to the Dark Side.

---

## 🏁 Get Creative With Your Pipelines

Did we still have to build dedicated repair functions into our Python scripts? Absolutely. But we stopped fighting the same battles. The XML quiz bank problem described earlier in this repo was eventually solved permanently — we separated content authoring from schema enforcement using an HTML template and a dedicated Python converter. The full breakdown is in the Dev.to article linked below.

We went from an outline to a fully deployed 12-module Moodle package — with medical-grade imagery and interactive H5P activities — in under 3 hours. The pipeline has run three more courses since the quiz fix. Zero XML debugging sessions.

Strict structured JSON output isn't the only way to build an agentic pipeline. Think about what your exact use case requires, take a step back, and architect a custom solution around what the AI *excels* at producing.

And to be perfectly clear: **this architecture is not theoretical.** The repository you are looking at contains a substantial chunk of our actual AI prompting framework and the literal Python extraction script we run in production. While we aren't giving away our entire proprietary curriculum, we have provided enough of the raw build engine and AI personas to prove that we built this for real — and more importantly, to give you the exact foundation you need to start building your own.

**Stop fighting the tech. Start orchestrating the workflow.**

---

## 🏛️ Standing on Existing Shoulders

None of the management patterns in this repo were invented for AI.

AI agent team design is treated as a new problem requiring new solutions. It isn't. The operational challenges in running a production agent team — quality control, institutional memory, role boundaries, failure mode prioritization, knowledge transfer, coordination — are the same challenges in any specialized human workforce. Every one of them has an established solution from an adjacent discipline. The solutions just weren't labeled "for AI."

The architecture in this repo borrows from manufacturing quality engineering, software release governance, organizational management, compiler theory, aviation safety, educational psychology, and psychometrics. Below is the full catalog. When you build your own agent system, this list tells you where to look before you invent.

---

### The Catalog at a Glance

| Borrowed Tool | Origin Discipline | What It Solves in AI |
|---|---|---|
| **FMEA** (Failure Mode and Effects Analysis) | Aerospace/automotive manufacturing | Prioritizing which agent failure modes to fix first |
| **Root Cause Analysis (RCA)** | Quality engineering / Toyota Production System | Separating architectural fixes from behavioral ones when outcome ≠ expected |
| **Pareto Analysis** | Six Sigma | Identifying the 20% of failure checks causing 80% of quality problems |
| **Control Charts** | Statistical Process Control | Tracking AI pipeline quality trends across builds |
| **Signal/Noise Filtering** | Data quality management | Curating known-acceptable failures to prevent false positive pollution |
| **Design of Experiments (DOE)** | Statistical experimental design (Fisher, Taguchi) | Structuring multi-variable improvement experiments so outcomes can be attributed to causes |
| **Semantic Versioning** | Software release governance | Versioning agent persona files as they evolve |
| **Gate Architecture** | Aerospace/pharmaceutical manufacturing QA | Structuring mandatory human review before content advances |
| **Shift Left** | Software quality engineering | Running automated agent quality checks before the human sees content |
| **CAD Standard** | Legal/regulatory defensibility | Defining the quality benchmark: Correct, Accurate, Defensible |
| **Work Orders** | Manufacturing/field service operations | Structured correction briefs from human reviewer to AI agent |
| **Andon Cord** | Toyota Production System | Emergency pipeline halt when a specialist agent detects a critical safety defect mid-generation |
| **Test-Driven Development (TDD)** | Software engineering | Quality constraints and rubrics defined in Gates 1-2 before content generation begins in Gate 4.1 |
| **Just-In-Time Manufacturing (JIT)** | Toyota Production System | Image generation deferred to Gate 4b — after content is finalized — eliminating rework waste |
| **Telemetry and Observability** | IT operations | Gate Completion Summary exposes internal pipeline state so the human reviewer understands how the output was produced, not just what it is |
| **Separation of Duties** | Accounting / information security | Content agents cannot audit their own output — enforced structurally, not by instruction |
| **Knowledge Item System** | Library science / knowledge management | Institutional memory that survives agent recreation |
| **Job Description** | Human resources | Designing agent role, authority, and scope before writing any prompt |
| **New-Hire Onboarding** | Human resources | Activating a new agent instance into its role |
| **Preflight Checklist** | Aviation safety | State verification before every AI session |
| **Predecessor Archaeology** | Archaeology | Recovering institutional knowledge after agent loss |
| **Specialist Team Structure** | Organizational design | Bounded-authority agents — no generalist overlap |
| **Deference Rules** | Authority hierarchy / matrix org design | Who yields to whom on which domain |
| **Scope Limits** | Contract law / Statement of Work | Explicit NEVER sections — what an agent must not do |
| **Handoff Protocol** | Operations management / healthcare SBAR | Structured context transfer between agents at gate transitions |
| **Compiler Architecture** | Compiler theory | LLM generates content; Python compiler handles format compliance |
| **Graceful Degradation** | Fault tolerance engineering | HTML parses despite imperfection; JSON fails completely on one bad character |
| **REST API Design** | Web engineering | Standard LLM-to-system communication protocol |
| **Bloom's Taxonomy** | Educational psychology | Constraining AI assessment items to the correct cognitive level |
| **Job Task Analysis (JTA)** | HR / training design | Anchoring AI content to what practitioners actually do in the field |
| **Psychometric Quality Standards** | Psychometrics / credentialing science | DIF screening, Cronbach's Alpha targets, item discrimination for AI-generated quizzes |
| **Proof-of-Work Summary** | Software delivery / project management | Gate completion summary: structured evidence package the human reviews at each gate |

---

### Six Worth Expanding

#### FMEA — Failure Mode and Effects Analysis

FMEA prioritizes failure modes in manufacturing by multiplying **Severity × Occurrence × Detectability**. We applied it directly to AI pipeline quality:

```
Risk = Severity × Persistence × Recency
```

- **Severity**: BLOCKER = 4, FAIL = 3, WARN = 1
- **Persistence**: failure rate across all builds (0.0–1.0)
- **Recency**: time-weighted decay since last failure

High-risk checks get 🔴 in the AI's pre-session briefing. The AI triages its own attention based on data. The formula is FMEA. The vocabulary changed. The math did not.

---

#### Semantic Versioning — For Agent Personas

SemVer (MAJOR.MINOR.PATCH) was built for software library releases. The three levels map exactly to the three types of behavioral change in an AI agent:

| SemVer Level | Software | Agent Persona |
|---|---|---|
| MAJOR | Breaking API changes | Human-led architectural redesign of role or authority |
| MINOR | New backward-compatible feature | Agent's autonomous self-improvement (wrote a new rule after post-mortem) |
| PATCH | Bug fix | Targeted human micro-correction (tone fix, scope clarification) |

When an agent autonomously created its own style guide to externalize rules it kept forgetting — that was a `MINOR` bump. Three months later, a human can read the version history and know exactly when and why the agent changed its own behavior.

---

#### Job Description — Write This Before You Write a Prompt

The AI agent persona file *is* a job description. Not metaphorically — structurally:

| Job Description Section | Agent Persona Equivalent |
|---|---|
| Job title and reporting line | Agent name + deference hierarchy |
| Key responsibilities | Enumerated mandate list |
| Authority scope | What the agent decides independently |
| Out-of-scope exclusions | The explicit **NEVER** section |
| Performance standards | Quality criteria (CAD standard, Bloom's levels) |
| Communication style | Tone, register, persona voice rules |

**Design implication:** When building a new agent, start with a job description, not a prompt. The JD discipline forces answers to questions prompt engineers skip: What decisions does this agent make independently? What is explicitly outside its mandate? Who does it defer to, and on what domain?

An agent written without that discipline produces the same outcomes as a vague job description: drift, scope creep, authority conflicts.

---

#### Preflight Checklist — From Aviation to AI Session Start

Aviation invented the preflight checklist after the 1935 Boeing Model 299 crash demonstrated that modern aircraft had become too complex to fly from memory. Commercial aviation made checklists mandatory. The insight: state verification before consequential operations is not optional.

Our Pipeline Preflight Template is an HTML file every agent reads at session start before generating a single character. Three blocks:

```html
<!-- Block 1: Hard rules — scope limits, ambiguity protocol, HIL correction behavior -->
<div id="agent-directives" data-ambiguity="stop-and-ask" data-scope="T1-only">

<!-- Block 2: Machine-written pipeline state — course, gate, resume point -->
<div id="pipeline-state" data-resume-from="3.8" data-pipeline-status="HIL_PENDING">

<!-- Block 3: Human reviewer corrections — check ID, severity, exact action required -->
<div id="hil-corrections">
```

Memory is useless without activation. The preflight is the activation. Aviation solved this in 1935.

---

#### Compiler Architecture — Separate Content From Format

LLMs generate content fluently. They do not reliably generate content in formats requiring mechanical precision — JSON schema compliance, XML namespaces, SCORM packaging spec. The naive solution (prompt the LLM to produce the target format) fails at non-trivial rates at scale.

Compiler theory solved this in the 1950s: separate the source language (which programmers write) from the target language (which machines execute). Let a compiler handle the translation.

We applied it directly. LLM agents generate semantic HTML. An 80KB Python compiler (T2) ingests approved HTML and produces Moodle-compatible course packages (.mbz). The LLM never touches Moodle's internal XML format. The compiler never touches content. Separation of concerns. The attempt to have the LLM generate Moodle activity XML directly failed on every trial. (SCORM was equally unworkable.) The compiler pattern did not.

---

#### Graceful Degradation — Why HTML Beats JSON at Scale

This is fault tolerance engineering applied to AI output parsing.

```python
# HTML: fails gracefully — partial recovery from most malformation
soup = BeautifulSoup(html, 'html.parser')
data = soup.find('div', {'data-module': 'M01'})  # works even with stray chars

# JSON: fails completely — one bad character, zero recovery
data = json.loads(content)  # raises exception on single unescaped quote
```

A single unescaped quotation mark in a 4,000-word lesson — the kind a language model generates with non-trivial regularity — returns nothing from `json.loads()`. BeautifulSoup recovers everything around the bad character. Across 98 pipeline builds: HTML parsing failures in 3 (3.1%), all auto-recovered. Predecessor JSON architecture: ~18% requiring manual intervention or lesson regeneration.

---

### The Design Checklist

Before you design a custom solution for your agent system, ask which discipline already solved it:

| Problem | Where to Look |
|---|---|
| How do I prioritize which failures to fix? | FMEA, Six Sigma, Pareto |
| A failure keeps recurring and I don't know why? | Root Cause Analysis — 5 Whys, Ishikawa diagram |
| How do I define a new agent role? | Write a job description first |
| How do I enforce role boundaries? | Organizational authority structures, Statements of Work |
| How do I keep agents from forgetting? | Knowledge management, institutional memory |
| How do I activate an agent correctly every session? | Preflight checklist (aviation) |
| How do I bring a new agent instance up to speed? | New-hire onboarding |
| How do I track whether quality is improving? | Control charts, Six Sigma SPC |
| How do I version agent behavior changes? | Semantic Versioning |
| How do I structure human review? | Gate architecture (aerospace QA) |
| How do I pass context between agents? | Operational handoff protocols (healthcare SBAR) |
| How do I ensure LLM output is in a reliable format? | Compiler theory — separate content from format |
| How do I generate valid assessment items? | Bloom's Taxonomy, JTA, psychometrics |
| Making multiple simultaneous system changes? | Design of Experiments — design before you change |

In most cases, the answer is not "design a custom solution." It is "implement the established solution with AI-appropriate tooling."

---

### The Paper

A full academic treatment of these thirty-two cross-domain tool applications — with production data, structural mappings, and the argument for the workforce framing of AI agent design — is in preparation. When published, it will be linked here.

The core argument: **AI agent teams are managed. The management problem is not new. The tools already exist.**

> *"None of this was invented from scratch. The entire system is built on existing tools and frameworks designed for software engineering and industrial process management. We just applied them to a workforce that happens to be AI."*
> — E. Fife, [My AI Remembers Its Mistakes](https://dev.to/edfife)

---

## 📝 Further Reading

These articles document the evolution of this architecture:

1. 📝 **[My AI Agents Version Themselves: How We Built Self-Evolving Personas Using Semantic Versioning](https://dev.to/edfife/my-ai-agents-version-themselves-how-we-built-self-evolving-personas-using-semantic-versioning-d9b)** — How our agents started teaching themselves to be better, and why we had to invent version control for behavior, not code.

2. 📝 **[Your AI Is Doing the Wrong Job. That's On You.](https://dev.to/edfife/your-ai-is-doing-the-wrong-job-thats-on-you-3182)** — What two weeks of Moodle import errors taught us about right-sizing roles. Includes the open source HTML quiz template and Python converter.

3. 📝 **[My AI Remembers Its Mistakes. Permanently. Here's the Engineering.](https://dev.to/edfife/my-ai-remembers-its-mistakes-permanently-heres-the-engineering-587h)** — Agent memory is not RAG. It is a measurement system — a closed feedback loop where every build produces forensic data that becomes persistent knowledge.

4. 📝 **[I Built My Own Review Pipeline Because My Humans Kept Making Me Redo Things](https://dev.to/edfife/i-built-my-own-review-pipeline-because-my-humans-kept-making-me-redo-things-3b0f)** — How an AI agent designed a file-bus architecture to survive its own users, with paragraph-level flagging and surgical corrections.

<br>

<div align="center">
  <i>(My AI approves this message.)</i><br>
</div>

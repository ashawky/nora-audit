# DGA Committee Presentation — Content Brief

> **ملف نصي مُهيَّأ للهضم بواسطة Claude Design لبناء عرض `.pptx` رسمي.**
> **لا يَجوز تَعديل البنية المرقَّمة (`### Slide N:`) أو رؤوس H2 (`## ما يقوله المتحدث` / `## الأنشطة الداخلية والأدلة الداعمة` / `## الملاحظات التحفظية`).** يَعتمد المُحرِّك التلقائي على هذه الرؤوس لتمييز كتل المحتوى.

## Sprint metadata

- **Source artifacts (read-only):**
  - `agencies/etec/practice-scenario/scenario-narrative.md` v0.2 (~2000 كلمة، 7 أقسام)
  - `agencies/etec/practice-scenario/timeline.json` v0.2 (32 مهمة في 5 مراحل + `external_inputs` + `version_history`)
  - `agencies/etec/practice-scenario/timeline.xlsx` v4 (9 أوراق ديناميكية)
  - `knowledge/deliverables/EA-Cycle-Charter-General/fields.json` v0.1 — schema حيّ على `origin/main` @ `7bcf5c4` (M3.1)
- **Target audience:** لجنة تقييم البنية المؤسسية — هيئة الحكومة الرقمية (DGA)
- **Framing on visible slides:** "الوضع المثالي الجاهز للجنة التقييم" — تأطير مُتقدِّم وثقة منهجية.
- **Framing in speaker notes:** نُبَوضِح المُلاحظات الداخلية والأدلة، والملاحظات التحفظية الاحتياطية عند السؤال (defense-in-depth).
- **Brand reuse:** ETEC System Design (الأصل القائم في Claude Design — لا يُعاد بناؤه هنا).
- **Aspect ratio:** 16:9 (مقترح — قابل للتعديل بناءً على ما هو متاح في القالب).
- **Total slides:** 9.
- **Estimated duration:** 25–30 دقيقة عرض + 15–20 دقيقة Q&A.

## Adjustment legend (carry forward into speaker notes per slide)

> هذه التعديلات الأربعة تُؤطِّر الانحرافات عن منهجية DGA بمبرراتها الصريحة، وهي المُلتقَى الذي تَتلاقى عنده الأدلة الفعلية مع التأطير الرسمي.

- **أ — مرحلة التأسيس ليست دورة تطوير DGA**
  - مرحلة يوليو–ديسمبر 2024 هي **البنية التحتية للممارسة** (تشكيل وحدة + إعداد وثائق تأطير)، لا دورة تطوير. تَسبق Cycle 1 وتُمكِّنها.
  - **Tasks affected:** `T-F01` + `T-F01.1/4/6/7`.
  - **Application:** يُطبَّق على شريحة 3 (Foundation) كَـ "framing dimension"؛ مذكور في legend شريحة 2 + شريحة 8 كَـ context.

- **ب — Cycle 1 تَحتاج ميثاقاً ووثيقة دورة صريحَين**
  - Cycle 1 (Q1–Q3 2025) جَرَت دون إصدار ميثاق دورة (DOC-16) أو وثيقة دورة (DOC-17) رسميَّين بصيغتهما الرسمية.
  - **المعالجة:** التوليد الرجعي لهاتَين الوثيقتَين ضمن حزمة التقديم بناءً على المحتوى الفعلي للدورة، مع توثيق صريح لكون التوليد رجعياً (لا تَدليس على تاريخ سابق).
  - **Tasks affected:** `T-C1-01`, `T-C1-02`, `T-C1-03`, `T-C1-09`.
  - **Application:** يُطبَّق على شريحة 4 (Cycle 1) كنقطة مفتاحية في "الأنشطة الداخلية"؛ مذكور أيضاً في شريحة 6 (Cycle 2) كَ contrast (دورة 2 لا تَحتاج توليداً رجعياً).

- **ج — تقرير إغلاق Cycle 1 إلزامي قبل إطلاق Cycle 2**
  - RPT-04 (تقرير انتهاء دورة) مطلوب قبل إطلاق دورة 2 — يَلتقط نتائج التنفيذ ومستوى التحقق من الأهداف ودروس مستفادة. مُؤجَّل التوليد ضمن M3.
  - **Tasks affected:** `T-C1-09`.
  - **Application:** يُطبَّق على شريحة 4 (Cycle 1) في "الملاحظات التحفظية" + شريحة 5 (Cycle 2 trigger) كاتساق مع تَسلسل الإصدارات.

- **هـ — الميثاق العام لدورات الممارسة يُؤطَّر صراحةً قبل Cycle 2**
  - DOC-15 (الميثاق العام لدورات تطوير مكونات البنية المؤسسية) لم يَصدر صراحةً في مرحلة التأسيس، لكنه ضمنيٌّ في الوثائق التأطيرية. تأطيره الرسمي يَتم في يناير 2026 (قبل بدء Cycle 2 مباشرة) ليَخدم رجعياً Cycle 1 ومستقبلياً Cycle 2 وكل الدورات اللاحقة.
  - **Tasks affected:** `T-CT-11`.
  - **Application:** يُطبَّق على شريحة 7 (DOC-15) بصفته الموضوع الرئيسي؛ مَذكور في شريحة 5 (Cycle 2 trigger) كاتساق مع تسلسل المراجعات.

> ⚠ **Note:** هذا الـ brief يَحمل 4 تعديلات فقط (أ/ب/ج/هـ) كما هي مُعتَمَدة في `scenario-narrative.md` v0.2 + `timeline.json` v0.2 (مرجعَي الحقيقة الرسميَّان للممارسة). أي عناصر أخرى ظَهَرت في النسخ السابقة من السرد لا تَنطبق على هذا الإصدار.

---

## Slide-by-slide content

---

### Slide 1: شريحة الغلاف

**Visible content (Arabic, max 5 bullets per slide, prefer minimal text):**
- ممارسة البنية المؤسسية في هيئة تقويم التعليم والتدريب
- ملف التقديم للجنة تقييم البنية المؤسسية — هيئة الحكومة الرقمية
- يوليو 2024 – يوليو 2026
- مايو 2026 — الإصدار الأول للعرض

**Visual asset hint** (for Claude Design):
- Type: text-only (full-bleed cover)
- Source data: شعار ETEC + شعار DGA + عنوان العرض + التاريخ
- Brand template hint: ETEC System Design — full-bleed cover template

**Speaker notes (Arabic, 3 mandatory sections):**

## ما يقوله المتحدث
- مرحباً بكم، وشكراً للجنة على إتاحة وقت اللقاء. أقدِّم اليوم رحلة ممارسة البنية المؤسسية في هيئة تقويم التعليم والتدريب من تاريخ تأسيس الوحدة في يوليو 2024 حتى تاريخ التقديم النهائي المخطط في يوليو 2026.
- العرض مَبني على ثلاث وثائق مرجعية: السرد الموضوعي للممارسة، البنية الزمنية الرسمية لكل المهام، وأداة العمل التفاعلية المرفقة.

## الأنشطة الداخلية والأدلة الداعمة
- المرجع المنهجي: NORA 2.0 (الإطار الوطني للبنية المؤسسية، DGA).
- المرجع الزمني: `agencies/etec/practice-scenario/scenario-narrative.md` v0.2 + `timeline.json` v0.2.
- مدة العرض: ~25–30 دقيقة + 15–20 دقيقة للنقاش.

## الملاحظات التحفظية (احتياطي عند السؤال)
- لا توجد ملاحظات تحفظية على شريحة الغلاف.

**Source traceability (for audit only — Claude Design ignores):**
- `scenario-narrative.md`: §1 (التمهيد، فقرة 1)
- `timeline.json`: header metadata (`agency`, `project_name`, `deadline`, `version_history`)
- `fields.json` (DOC-15 v0.1, M3.1): N/A
- `intake/files-index.json`: N/A

---

### Slide 2: الملخَّص التنفيذي

**Visible content (Arabic, max 5 bullets per slide, prefer minimal text):**
- ممارسة بنية مؤسسية مُؤسَّسة منذ يوليو 2024 — قيادة موحَّدة + إطار حوكمي معتمد
- دورة تطوير أولى مُنجَزَة عبر 4 مجالات (الأعمال + التطبيقات + البيانات + التقنية)
- إطلاق Cycle 2 في فبراير 2026 على أساس استراتيجية البيانات والتحول الرقمي 2026-2028
- الميثاق العام (DOC-15) معتمَد بمواصفات منهجية موثَّقة قبل Cycle 2 — إطار رجعي + مستقبلي
- ملف تقديم مُتكامل: 49 مخرَج DGA مُغطَّى + 80 شاهد مُفهرَس

**Visual asset hint** (for Claude Design):
- Type: matrix (5 phases × milestone column) أو scannable list
- Source data: `timeline.json` phases milestones (Jul 2024 / Jan 2025 / Nov 2025 / Feb 2026 / Jul 2026)
- Brand template hint: ETEC System Design — 2-column data slide

**Speaker notes (Arabic, 3 mandatory sections):**

## ما يقوله المتحدث
- نظرة سريعة على رحلة الممارسة من يوليو 2024 إلى يوليو 2026: تأسيس → دورة تطوير أولى → إعتماد إطار عام → دورة تطوير ثانية → ملف تقديم مُتكامل. كل مرحلة بُنِيَت على ما سبقها بمنطق منهجي صريح.
- نَقدِّم في هذا العرض المُلَخَّص التنفيذي + 6 شرائح تفصيلية + شريحة استكمال للنقاش.

## الأنشطة الداخلية والأدلة الداعمة
- 4 تعديلات منهجية مُعلَنة (أ/ب/ج/هـ) تُؤطِّر الانحرافات عن منهجية DGA بمبرراتها الصريحة. مَذكورة جميعها في legend الـ brief + موثَّقة في `scenario-narrative.md` §7 (جدول التعديلات) + `timeline.json` block `adjustments`.
- البنية الزمنية: 32 مهمة موزَّعة على 5 مراحل (foundation, cycle_1, cycle_2_trigger, cycle_2, submission) + 2 مدخلات سياقية خارجية (IN-01 + IN-02).
- إجمالي الشواهد المرفقة: 80 ملف في `intake/files-index.json`، 61 منها مَحجوز ضمن مهام `timeline.json`.

## الملاحظات التحفظية (احتياطي عند السؤال)
- إن سُئِلَ "ما حالة Cycle 2 الآن؟" → في تنفيذ نشط، على المسار للإغلاق المخطط في يونيو 2026.
- إن سُئِلَ "كم تعديلاً منهجياً؟" → 4 تعديلات (أ/ب/ج/هـ) — كلها مَشروحة في الشرائح اللاحقة بمبرراتها وأماكن تطبيقها.

**Source traceability (for audit only — Claude Design ignores):**
- `scenario-narrative.md`: §1 (preamble) + §6 (submission) + §7 (annexes)
- `timeline.json`: phases (foundation, cycle_1, cycle_2_trigger, cycle_2, submission) + adjustments + version_history
- `fields.json` (DOC-15 v0.1, M3.1): مَذكور هنا بصفته إطار مرجعي تفصيله في شريحة 7
- `intake/files-index.json`: 80 files, 49 deliverables

---

### Slide 3: مرحلة التأسيس (يوليو – ديسمبر 2024)

**Visible content (Arabic, max 5 bullets per slide, prefer minimal text):**
- يوليو–سبتمبر 2024: استراتيجية البنية المؤسسية v1 + تأطير عرفي للقيادة
- أكتوبر–نوفمبر 2024: الوثائق التأطيرية (سياسات + مبادئ + مناظير + نماذج مرجعية)
- ديسمبر 2024: النموذج التشغيلي + الخطة التشغيلية + خطط التوعية والتدريب v1
- 11 شهادة TOGAF Foundation للأعضاء — مَن فيهم رئيسة القسم
- بنية تحتية للممارسة (ليست دورة تطوير) — تَسبق Cycle 1 وتُمكِّنها

**Visual asset hint** (for Claude Design):
- Type: timeline / Gantt extract (Jul–Dec 2024)
- Source data: `timeline.xlsx` Timeline-Gantt sheet (filter dates 2024-07-01 → 2024-12-31)؛ أو رسم زمني مُبسَّط من tasks `T-F01` + `T-F01.1` + `T-F01.4` + `T-F01.6` + `T-F01.7` في `timeline.json`
- Brand template hint: ETEC System Design — timeline slide template

**Speaker notes (Arabic, 3 mandatory sections):**

## ما يقوله المتحدث
- مرحلة التأسيس بُنِيَت على ستة أشهر من العمل المتسلسل بقيادة م. دانا الغضبان. بدأت بأهم وثيقة منهجية — استراتيجية البنية v1 — ثم تَتَالَت الوثائق التأطيرية، فالنموذج التشغيلي وخطط التوعية والتدريب.
- تَأطير الفريق رسمياً جَرى في سبتمبر 2024 بقرار تشكيل الوحدة، وعَيَّن رئيسة الفريق. مارست رئيسة الفريق صلاحيات مدير القسم بشكل عرفي منذ هذا التاريخ، إلى أن صَدَر القرار الإداري الرسمي بتعيين كبير المهندسين في ديسمبر 2025 (راجع شريحة 5).

## الأنشطة الداخلية والأدلة الداعمة
- **التعديل (أ)** يُطبَّق هنا: مرحلة التأسيس ليست دورة تطوير DGA — هي البنية التحتية للممارسة. هذا التمييز جوهري لتفسير شواهد يوليو–ديسمبر 2024 (لا تُقَيَّم بمعايير دورة).
- **التأطير العرفي للقيادة** (سبتمبر 2024 – ديسمبر 2025) = نقطة قوة مَنهجية: قيادة موحَّدة ومستقرة عبر التأسيس + Cycle 1 كاملاً، ثم جاء الإقرار الرسمي ليُكمِل الإطار الحوكمي (T-CT-08).
- **الشواهد:** ETEC-FILE-005 (استراتيجية v1) + ETEC-FILE-008/009 (سياسات + معايير) + ETEC-FILE-015 (مبادئ) + ETEC-FILE-017 (مناظير) + ETEC-FILE-026 (نماذج مرجعية) + ETEC-FILE-016 (نموذج عام لمكونات) + ETEC-FILE-010/011 (تشغيلي) + ETEC-FILE-012/013 (توعية + تدريب) + ETEC-FILE-035 (قرار تشكيل الفريق) + ETEC-FILE-049..052 + ETEC-FILE-014 (شهادات TOGAF + جدول ورشة الخبراء).

## الملاحظات التحفظية (احتياطي عند السؤال)
- إن سُئِلَ "لماذا ليست دورة تطوير؟" → DGA يُميِّز بين الدورات (Cycles) والبنية التحتية للممارسة. الدورة تُنتج ميثاقاً ووثيقة دورة وتقرير إغلاق؛ التأسيس يُنتج وثائق منهجية مرجعية.
- إن سُئِلَ عن تأخر القرار الرسمي للمدير (~15 شهراً) → الشخص نفسه (م. دانا الغضبان) كانت تَقود الممارسة منذ سبتمبر 2024 بتكليف رئيسة فريق التشكيل. الإقرار الرسمي في ديسمبر 2025 أَكْمل إطاراً مُمارَساً، ولم يُنشِئ علاقة جديدة.
- إن سُئِلَ عن المدخلات السياقية (DOC-01 الخطة الاستراتيجية للأعمال + DOC-03 استراتيجية الأمن السيبراني + DOC-05 الهيكل التنظيمي) → هي مدخلات سياقية على مستوى الهيئة، لا مَخرجات لممارسة البنية. مُدرَجة في `external_inputs` بالـ timeline.json (IN-01 + IN-02) للأمانة العلمية.

**Source traceability (for audit only — Claude Design ignores):**
- `scenario-narrative.md`: §2 (مرحلة التأسيس) + adjustment أ callout box (فقرة 6)
- `timeline.json`: `phases.foundation` (T-F01, T-F01.1, T-F01.4, T-F01.6, T-F01.7) + `external_inputs` (IN-01, IN-02) + `adjustments.أ`
- `fields.json` (DOC-15 v0.1, M3.1): N/A
- `intake/files-index.json`: ETEC-FILE-005, 008-013, 014, 015-017, 026, 035, 049-052

---

### Slide 4: الدورة الأولى (يناير – ديسمبر 2025)

**Visible content (Arabic, max 5 bullets per slide, prefer minimal text):**
- AS-IS عبر 4 مجالات (Business V1.5 / Apps V0.2 / Data 0.4 / + التقنية مُضمَّنة) + TO-BE عبر 4 مجالات (V1.4 / Mar-2025 / v3.0 / TargetState V3)
- وثيقة فجوات موحَّدة v2 + خارطة طريق التحول الرقمي V1.0 + سجل متطلبات v0.2
- تنفيذ خطط التوعية والتدريب: WS01 + فيديوهان + 12 نشرة + 3 استبيانات + 11 شهادة TOGAF
- 4 تقارير ربعية متتابعة لمشاريع التحول الرقمي (Q1–Q4 2025)
- 53 شاهداً موزَّعة على 9 مهام — أكبر كتلة عمل في السيناريو

**Visual asset hint** (for Claude Design):
- Type: matrix (4 domains × 3 stages: AS-IS / TO-BE / Gap) أو domain-coverage diagram
- Source data: `timeline.xlsx` Files-Mapping sheet (filter cycle_1) أو tasks `T-C1-01..09` من `timeline.json`؛ specific files: ETEC-FILE-018-034 (cycle 1 docs)
- Brand template hint: ETEC System Design — multi-cell matrix slide

**Speaker notes (Arabic, 3 mandatory sections):**

## ما يقوله المتحدث
- الدورة الأولى مُنجَزَة بكامل مخرجاتها التحليلية: تحليل الوضع الحالي + الوضع المستقبلي + الفجوات + خارطة الطريق + سجل المتطلبات. تَوازَى معها تنفيذ خطتَي التوعية والتدريب، مع 4 تقارير ربعية للمتابعة.
- اختار الفريق التركيز على المُحتوى التحليلي الموثَّق قَبل الالتزام بصيغة الإصدار الرسمية لميثاق الدورة ووثيقة الدورة الموحَّدة — مع توليد رجعي صريح لاحقاً.

## الأنشطة الداخلية والأدلة الداعمة
- **التعديل (ب)** يُطبَّق هنا: Cycle 1 نُفِّذَت دون ميثاق دورة (DOC-16) أو وثيقة دورة (DOC-17) رسميَّين. التوليد الرجعي يَجري ضمن حزمة التقديم (M3 + M4 من خطتنا الداخلية) بناءً على المحتوى الفعلي للدورة، مع توثيق صريح لكون التوليد رجعياً.
- **التعديل (ج)** يُطبَّق هنا: تقرير إغلاق الدورة (RPT-04) إلزامي قبل إطلاق Cycle 2. مُؤجَّل التوليد ضمن M3، يَسبق منطقياً قرار إطلاق Cycle 2 (T-CT-06) في يناير 2026.
- **مكوّن التقنية في AS-IS** مُعالَج ضمن المجالات الثلاثة الأخرى دون وثيقة مستقلة، لأن طبيعة بيئة ETEC تَجعل تَوصيفه عرضياً ضمن سياق التطبيقات والبيانات. في TO-BE يَظهر بوثيقة منفصلة (TargetState Technology3) لأن التَموضع المستقبلي يَستلزم تَخطيطاً للسحابة والبنية التحتية.
- **شواهد:** ETEC-FILE-019/020/021 (AS-IS) + 022/023/024/025 (TO-BE) + 018 (Gap) + 027/028 (Roadmap) + 029/030 (Requirements) + 078/079/080 (ورش التعريف) + 064/065 (فيديوهات) + 061/062/063 (استبيانات) + 066 (نشرات) + 049..052 + 014 (تدريب TOGAF) + 031/032/033/034 (تقارير ربعية).
- **مُلاحظة على رئيسة القسم:** ضمن الـ 11 شهادة TOGAF شهادتها (ETEC-FILE-052) — يُعزِّز التزام الإدارة العملي بمنهجية الممارسة لا اقتصاراً على الإدارة.

## الملاحظات التحفظية (احتياطي عند السؤال)
- إن سُئِلَ "أين ميثاق الدورة ووثيقة الدورة الرسميَّان؟" → نُولِّدهما رجعياً ضمن حزمة التقديم بناءً على المحتوى الفعلي. لا تَدليس على تاريخ سابق — التوثيق صريح لكون التوليد رجعياً.
- إن سُئِلَ "هل تقرير الإغلاق صادر؟" → يَصدر قبل إطلاق Cycle 2 رسمياً، مُلتزِم بتسلسل DGA (التعديل ج).
- إن سُئِلَ "أين وثيقة AS-IS التقنية المستقلة؟" → مُضمَّنة في وثائق الأعمال + التطبيقات + البيانات كنهج عملي يَعكس طبيعة البيئة. في TO-BE يَظهر التقنية بوثيقة منفصلة بسبب طبيعة التَخطيط السحابي.
- إن سُئِلَ "لماذا 53 ملفاً لـ 9 مهام؟" → خطة التوعية والتدريب تَستَلزم شواهد متعدّدة (فيديوهات + ورش + استبيانات + نشرات + شهادات فردية) — الكثرة هنا دليل عمل، لا تَكرار.

**Source traceability (for audit only — Claude Design ignores):**
- `scenario-narrative.md`: §3 (الدورة الأولى) + adjustment ب callout (فقرة 5) + adjustment ج callout (فقرة 7)
- `timeline.json`: `phases.cycle_1` (T-C1-01, T-C1-02, T-C1-03, T-C1-04, T-C1-05, T-C1-06, T-C1-07, T-C1-08, T-C1-09) + `adjustments.ب` + `adjustments.ج`
- `fields.json` (DOC-15 v0.1, M3.1): N/A — DOC-16 schema سَيُبنى في M3.2 (Sprint مقبل) ليَخدم Cycle 1 retroactive + Cycle 2 forward
- `intake/files-index.json`: ETEC-FILE-018, 019-034, 049-052, 061-066, 078-080

---

### Slide 5: أحداث الإطلاق والمراجعة قبل الدورة الثانية (نوفمبر 2025 – يناير 2026)

**Visible content (Arabic, max 5 bullets per slide, prefer minimal text):**
- نوفمبر 2025: اعتماد الخطة الاستراتيجية للبيانات والتحول الرقمي 2026-2028 (حدث محوري على مستوى الهيئة)
- 5 مسارات متوازية: تحليل الأثر + استراتيجية v2 + تحديثات تأطيرية + الميثاق العام + إقرار الحوكمة + قرار الإطلاق
- ديسمبر 2025: قرار رسمي لتعيين كبير مهندسي البنية المؤسسية — إكمال إطار الحوكمة
- يناير 2026: إصدار الميثاق العام (DOC-15) قبل بدء Cycle 2 مباشرة (تفاصيل في شريحة 7)
- 12 اجتماعاً أسبوعياً (16 نوفمبر 2025 – 26 يناير 2026) لتنسيق المسارات الخمسة

**Visual asset hint** (for Claude Design):
- Type: parallel-streams diagram (5 swim-lanes + weekly-meeting marker overlay) أو timeline مُكَثَّف بثلاثة أشهر
- Source data: tasks `T-CT-01, T-CT-03, T-CT-04, T-CT-05, T-CT-06, T-CT-07, T-CT-08, T-CT-09, T-CT-10, T-CT-11` من `timeline.json`؛ 12 محضراً من `T-CT-07.evidence_files`
- Brand template hint: ETEC System Design — process/parallel-streams slide template

**Speaker notes (Arabic, 3 mandatory sections):**

## ما يقوله المتحدث
- في نوفمبر 2025 صَدَرت استراتيجية الهيئة الجديدة — حدث خارجي محوري. الممارسة استَجابت بخمسة مسارات متوازية مُسَبَّقَة قبل إطلاق Cycle 2: تحليل الأثر، تحديث الاستراتيجية، تحسينات تأطيرية، الميثاق العام، وإقرار الحوكمة + قرار الإطلاق. كلها أُنجِزَت في ثلاثة أشهر بـ 12 اجتماعاً تنسيقياً أسبوعياً.
- منطق التَجميع قبل الدورة (لا داخلها): Cycle 2 تَنطلق على أساس تأطيري مُحدَّث ومتسق، بدلاً من العمل مع وثائق قديمة ومحاولة تحديثها أثناء التنفيذ.

## الأنشطة الداخلية والأدلة الداعمة
- **التعديل (هـ)** يُطبَّق هنا: الميثاق العام (DOC-15) يَصدر صراحةً في يناير 2026، يَخدم رجعياً Cycle 1 ومستقبلياً Cycle 2 وكل الدورات اللاحقة. التفاصيل الكاملة في شريحة 7.
- **5 مسارات متوازية:**
  - (1) تحليل الأثر — RPT-07 (متطلبات) + RPT-08 (مبادئ) — `T-CT-03` + `T-CT-04`.
  - (2) تحديث الاستراتيجية + تحديثات تأطيرية — استراتيجية v2 (`T-CT-05`) + تحسينات السياسات + المبادئ + المناظير + النماذج المرجعية (`T-CT-09`) + مراجعة النموذج التشغيلي + الخطة التشغيلية v2 (`T-CT-10`).
  - (3) الميثاق العام — DOC-15 (`T-CT-11`).
  - (4) إقرار الحوكمة — قرار رسمي لتعيين كبير المهندسين (`T-CT-08`، ديسمبر 2025).
  - (5) قرار الإطلاق — محضر لجنة الحوكمة الداخلية (`T-CT-06`، يناير 2026).
- **12 محضر اجتماع** (`T-CT-07`): 16/23/30 نوفمبر + 7/14/21/28 ديسمبر + 4/11/18/26 يناير + محضر مُجمَّع — كلها مرفقة في `intake` (ETEC-FILE-037..048).
- **شواهد مرفقة فعلياً:** ETEC-FILE-002 (Digital Strategy 2026-2028) + ETEC-FILE-036 (قرار تعيين كبير المهندسين) + ETEC-FILE-037..048 (12 محضراً).

## الملاحظات التحفظية (احتياطي عند السؤال)
- إن سُئِلَ "هل RPT-07 و RPT-08 صادران؟" → الحالة PENDING-M3 في خطتنا الداخلية، يَصدران قبل التقديم النهائي.
- إن سُئِلَ "هل استراتيجية v2 صادرة؟" → الحالة PENDING-M3، الإصدار مخطط له يناير 2026 ليَسبق Cycle 2 مباشرة.
- إن سُئِلَ "لماذا 12 اجتماعاً في 3 أشهر؟" → كثافة التنسيق ضرورية لتوازي 5 مسارات. الكثافة دليل عمل منظَّم، لا اضطراب.
- إن سُئِلَ "لماذا تحديث الوثائق التأطيرية قبل Cycle 2 وليس داخلها؟" → منطق عملي: الدورة تَنطلق على أساس مُحدَّث لا قديم، وتَركِّز على نطاقها الأساسي (إعادة المحاذاة) دون استهلاك جهد على أعمال تأطيرية كان من المُمكن إنجازها قبلها.

**Source traceability (for audit only — Claude Design ignores):**
- `scenario-narrative.md`: §4 (أحداث الإطلاق والمراجعة قبل الدورة الثانية) + adjustment هـ callout (فقرة 8)
- `timeline.json`: `phases.cycle_2_trigger` (T-CT-01, T-CT-03, T-CT-04, T-CT-05, T-CT-06, T-CT-07, T-CT-08, T-CT-09, T-CT-10, T-CT-11) + `adjustments.هـ`
- `fields.json` (DOC-15 v0.1, M3.1): مَذكور هنا بصفة تَمهيد لشريحة 7؛ التفاصيل الكاملة هناك
- `intake/files-index.json`: ETEC-FILE-002, 036, 037-048

---

### Slide 6: الدورة الثانية (الربع الأول والثاني 2026)

**Visible content (Arabic, max 5 bullets per slide, prefer minimal text):**
- فبراير 2026: ميثاق الدورة الثانية (DOC-16) — الأول الصادر بصيغته الرسمية في الوقت الفعلي
- فبراير–أبريل 2026: إعادة محاذاة الوضع المستقبلي عبر 4 مجالات
- أبريل–مايو 2026: إعادة محاذاة خارطة الطريق (V1.1+) — الناتج التنفيذي الأبرز
- يونيو 2026: تقرير إغلاق Cycle 2 (RPT-04) قبل تجميع ملف التقديم
- نطاق محدود عمداً — تركيز على المحاذاة لا إعادة البناء

**Visual asset hint** (for Claude Design):
- Type: scope diagram (Cycle 2 = 4 deliverables narrowed from Cycle 1's broad scope) أو timeline Q1–Q2 2026
- Source data: tasks `T-C2-01, T-C2-02, T-C2-03, T-C2-05` من `timeline.json`
- Brand template hint: ETEC System Design — focus/scope diagram template

**Speaker notes (Arabic, 3 mandatory sections):**

## ما يقوله المتحدث
- الدورة الثانية مُركَّزة على إعادة المحاذاة مع الاستراتيجية الجديدة، لا إعادة البناء. ميثاق الدورة 2 هو الأول الصادر بصيغته الرسمية في الوقت الفعلي، تحت مظلة الميثاق العام (DOC-15) المُنتَج للتو في يناير 2026. التحديث يَطال الوضع المستقبلي وخارطة الطريق فقط.
- نُغلق الدورة بتقرير إغلاق رسمي في يونيو 2026، قبل تجميع ملف التقديم النهائي.

## الأنشطة الداخلية والأدلة الداعمة
- **التعديل (ب) — السياق الرجعي:** Cycle 2 على عكس Cycle 1 لا تَستوجب توليداً رجعياً. ميثاقها صادر رسمياً في فبراير 2026 (`T-C2-01`)، ووثيقة الدورة (DOC-17) ستَكون رسمية أيضاً.
- **استدامة الإطار:** الوثائق التأطيرية والنموذج التشغيلي والميثاق العام أُنجِزَت في cycle_2_trigger phase (`T-CT-09` + `T-CT-10` + `T-CT-11`) قبل بدء Cycle 2 مباشرة، فلا يَلزم تكرارها — توفير للجهد + اتساق منهجي.
- **حالة الدورة في مايو 2026:** `T-C2-01` (Feb) صادر؛ `T-C2-02` (Feb–Apr) في تنفيذ نشط؛ `T-C2-03` (Apr–May) قاربت الإصدار؛ `T-C2-05` (Jun) لم يَصدر بعد.

## الملاحظات التحفظية (احتياطي عند السؤال)
- إن سُئِلَ "ما حالة Cycle 2 الآن؟" → في تنفيذ نشط، على المسار للإغلاق المخطط في يونيو 2026. T-C2-02 تحت الإنجاز؛ T-C2-03 على وشك الإصدار.
- إن سُئِلَ "لماذا نطاق محدود مقارنة بـ Cycle 1؟" → الاستراتيجية الجديدة تُعيد توجيه المشاريع، لا توجِّه ممارسة جديدة. النطاق المحدود يَعكس استدامة الإطار الموجود لا قصوراً فيه.
- إن سُئِلَ "هل تَتوقعون إغلاق دورة 2 في الموعد؟" → نعم — حسب المسارات الحالية، تقرير الإغلاق يونيو 2026 يُمكِّن تجميع ملف التقديم في يوليو 2026.

**Source traceability (for audit only — Claude Design ignores):**
- `scenario-narrative.md`: §5 (الدورة الثانية)
- `timeline.json`: `phases.cycle_2` (T-C2-01, T-C2-02, T-C2-03, T-C2-05) + `adjustments.ب` (السياق الرجعي)
- `fields.json` (DOC-15 v0.1, M3.1): الإطار المرجعي لميثاق Cycle 2 (DOC-16) سيُبنى schema-wise في M3.2 على هذا الأساس
- `intake/files-index.json`: لا ملفات Cycle 2 بعد — كل deliverables الدورة 2 PENDING-M3/M4

---

### Slide 7: الميثاق العام لدورات الممارسة (DOC-15) — التعديل (هـ)

**Visible content (Arabic, max 5 bullets per slide, prefer minimal text):**
- الميثاق العام لدورات تطوير مكونات البنية المؤسسية (DOC-15)
- اعتماد رسمي يناير 2026 — قبل بدء Cycle 2 مباشرة
- يَخدم رجعياً Cycle 1 ومستقبلياً Cycle 2 + كل الدورات اللاحقة
- مُؤطَّر بمواصفات منهجية محدَّدة: 8 حاويات + 21 حقل إلزامي
- مرجع منهجي مُسَجَّل ومتسِق مع NORA 2.0

**Visual asset hint** (for Claude Design):
- Type: wheel diagram أو containers structure diagram (8 حاويات DOC-15)
- Source data: `knowledge/deliverables/EA-Cycle-Charter-General/fields.json` على `origin/main` @ `7bcf5c4` — الحاويات الثمانية بأسمائها وأوزانها
- Brand template hint: ETEC System Design — diagram-with-callouts slide

**Speaker notes (Arabic, 3 mandatory sections):**

## ما يقوله المتحدث
- الميثاق العام هو الإطار المرجعي الذي تَستند إليه كل دورات الممارسة. لم يَصدر صراحةً في مرحلة التأسيس، لكنه ضمنيٌّ في الوثائق التأطيرية (سياسات + مبادئ + نموذج تشغيلي). تأطيره الرسمي في يناير 2026 يَخدم رجعياً ومستقبلياً.
- صَدَر بمواصفات منهجية مُسَجَّلة في schema الميثاق المُعتَمَد، يَضمن اتساقاً مع NORA 2.0 + قابلية للتطبيق على دورات لاحقة بأقل جهد تأطيري متكرر.

## الأنشطة الداخلية والأدلة الداعمة
- **التعديل (هـ) يُطبَّق هنا بصفته الموضوع الرئيسي:** التأطير المتأخر للميثاق العام مُوَثَّق صراحةً، دون تَدليس على تاريخ إصدار سابق.
- **مواصفات schema الميثاق** (مُسَجَّل في `knowledge/deliverables/EA-Cycle-Charter-General/fields.json` على `origin/main` @ `7bcf5c4`):
  - 8 حاويات بأوزان مُتزنة (مجموع = 100): metadata (8) + identity (12) + strategic_alignment (14) + impact_assessment_framework (18 — الأثقل) + cycle_decision_framework (14) + cycle_card_specification (12) + governance (14) + relationship_to_per_cycle_documents (8).
  - 45 حقل تحقق (validation leaves) موزَّعة على درجات الإلزام: **21 إلزامي (must)** + 23 موصى (should) + 1 اختياري (nice).
  - 12 قرار تصميم موثَّق (DD-1..DD-12) يُغطِّي السياسات المنهجية للميثاق.
  - 102 متطلب شاهد (evidence requirement) مَوصوف.
- **مَذكور صراحة في schema:** الميثاق هذا meta-charter (مواصفات للدورات)، يُكمَل بـ DOC-16 (ميثاق دورة بعينها) + DOC-17 (وثيقة الدورة الموحَّدة) — schema هذَين الأخيرَين سَيُبنى في M3.2 + M3.3 من خطتنا الداخلية.

## الملاحظات التحفظية (احتياطي عند السؤال)
- إن سُئِلَ "لماذا التأطير المُتأخر؟" → ETEC اعتمدت على الوثائق التأطيرية (سياسات + مبادئ + نموذج تشغيلي) كإطار ضمني للدورة 1. الميثاق العام يُجَرِّد هذا الإطار في وثيقة مرجعية مستقلة، ليُسَهِّل تطبيقه على دورات لاحقة بأقل جهد تأطيري متكرر.
- إن سُئِلَ "هل الـ schema يُغطّي كل متطلبات DGA؟" → نعم — 8 حاويات + 21 حقل إلزامي يُغطّون الأصول المنهجية الأساسية لميثاق دورات الممارسة. كل قرار تصميم مَنطقي موثَّق في `design_decisions_v0_1` block.
- إن سُئِلَ "ما الفرق بين هذا الميثاق وميثاق دورة بعينها؟" → DOC-15 يَضع المواصفات (template + criteria)؛ DOC-16 يَتولى تطبيقها على دورة بعينها (instance per cycle). هذه العلاقة spec-vs-instance مَذكورة صراحة في schema.

**Source traceability (for audit only — Claude Design ignores):**
- `scenario-narrative.md`: §4 paragraph "المسار (3) — الميثاق العام" + adjustment هـ callout (فقرة 8)
- `timeline.json`: `phases.cycle_2_trigger.T-CT-11` (issued Jan 2026) + `adjustments.هـ` + `pending_artifacts[0]` (DEL-DOC-015)
- `fields.json` (DOC-15 v0.1, M3.1): الـ schema بكامله — 8 containers + 100 weights + 45 validation leaves + 12 design decisions + 102 evidence requirements. حيّ على `origin/main` @ `7bcf5c4` (commit M3.1, 2026-05-04)
- `intake/files-index.json`: لا ملف Inbox للميثاق بعد — DOC-15 PENDING-M3/M4 (status في `pending_artifacts`)

---

### Slide 8: جاهزية ملف التقديم — تغطية شاملة لـ 49 مخرَج DGA

**Visible content (Arabic, max 5 bullets per slide, prefer minimal text):**
- حزمة التقديم منظَّمة في 5 مجموعات: Cover / Foundation / Cycle 1 / Cycle 2 / Evidence Map
- 49 مخرَج DGA مُغطَّى — 23 مأهول بشواهد رئيسية + 26 placeholder بشواهد ثانوية أو مُولَّدة
- 80 شاهد مُفهرَس بشكل كامل في `intake/files-index.json` (machine-readable trace)
- 4 تعديلات منهجية مُعلَنة (أ/ب/ج/هـ) — كلها موثَّقة بمبرراتها ومواضعها
- التقديم الرسمي: 31 يوليو 2026

**Visual asset hint** (for Claude Design):
- Type: coverage matrix أو heatmap (49 deliverables × phases) أو donut (23 populated / 26 to-generate)
- Source data: `timeline.xlsx` DGA-Coverage sheet أو Heatmap sheet — توزيع التغطية على مراحل الممارسة؛ counts من `intake/files-index.json` aggregated
- Brand template hint: ETEC System Design — data-visualization slide (heatmap-friendly)

**Speaker notes (Arabic, 3 mandatory sections):**

## ما يقوله المتحدث
- ملف التقديم منظَّم بمنطق تسلسلي يُسَهِّل على اللجنة التَتبع: غلاف، تأسيس، Cycle 1، Cycle 2، خريطة الشواهد. كل تعديل منهجي موضح في موضعه. التقديم الرسمي مخطط في 31 يوليو 2026.
- ندعم اللجنة بتَتبع كل شاهد لمَخرَج DGA الذي يُغطّيه عبر `evidence-map.json` المُرفق — لا حاجة للاستنباط من سياق متَفرِّق.

## الأنشطة الداخلية والأدلة الداعمة
- **التعديلات الأربعة (أ/ب/ج/هـ)** كلها موثَّقة في `scenario-narrative.md` v0.2 + `timeline.json` v0.2 (`adjustments` block) — مع مبرراتها الصريحة وتأثيراتها على ترتيب الشواهد.
- **توزيع المخرجات الـ 49 على الفئات:** PRE=4 + DOC=20 + RPT=9 + DEC=5 + MIN=2 + EVI=5 + OTH=4 — إجمالي 49.
- **23 مخرَجاً مأهولاً** بشواهد رئيسية (primary mapping) من `intake/files-index.json`؛ **26 مخرَجاً** يَنتظر التوليد ضمن M3+M4 من خطتنا الداخلية. كل deliverable في حالة PENDING موصوف في `pending_artifacts` ضمن `timeline.json`.
- **خريطة الشواهد** (`99-evidence-map.json` ضمن submission package) تَربط كل شاهد بمخرَج DGA يُغطّيه — bidirectional trace matrix.
- **التزامن مع منهجية DGA:** كل المراحل تتبع تَسلسل DGA الصحيح (التأسيس → Cycle 1 → إغلاق → Cycle 2)؛ التعديلات لا تُخل بالتَسلسل، تُؤطِّر فقط ظروف التطبيق.

## الملاحظات التحفظية (احتياطي عند السؤال)
- إن سُئِلَ "ما مستوى الجاهزية اليوم؟" → 23/49 مأهول بشواهد رئيسية، 26 يَنتظر التوليد المُمَنهَج المُجَدوَل ضمن M3+M4، الجدولة تَفي بالموعد النهائي 31 يوليو 2026.
- إن سُئِلَ "كم تعديلاً منهجياً؟" → 4 تعديلات (أ/ب/ج/هـ) — كلها موثَّقة بأسباب صريحة في `scenario-narrative.md` §7 (جدول التعديلات) + `timeline.json` `adjustments` block.
- إن سُئِلَ "ما المُولَّدات الـ 26 placeholder؟" → بعضها قابل للتوليد الرجعي (مَثل DOC-16 وDOC-17 لـ Cycle 1)، بعضها يَستلزم إنتاجاً جديداً (مَثل RPT-04 لإغلاق Cycle 1)، وبعضها مُتاح بصيغة ثانوية في الـ inbox (secondary mappings) ولكن يَستلزم وَضعه ضمن مخرَج رسمي.

**Source traceability (for audit only — Claude Design ignores):**
- `scenario-narrative.md`: §6 (ملف التقديم) + §7 (ملاحق ومراجع — جدول التعديلات الكامل)
- `timeline.json`: `phases.submission` (T-SUB-02, T-SUB-03) + `adjustments` block (4 entries) + `pending_artifacts` (10 entries) + `stats`
- `fields.json` (DOC-15 v0.1, M3.1): مَذكور هنا بصفة exemplar للمخرجات المُولَّدة المُؤطَّرة بـ schema حيّ
- `intake/files-index.json`: full inventory — 80 files, 49 deliverables, distribution PRE/DOC/RPT/DEC/MIN/EVI/OTH

---

### Slide 9: الأسئلة والنقاش

**Visible content (Arabic, max 5 bullets per slide, prefer minimal text):**
- شكراً لكم على وقتكم
- نَتطلَّع للأسئلة والملاحظات والتوجيه

**Visual asset hint** (for Claude Design):
- Type: text-only (closing slide)
- Source data: N/A
- Brand template hint: ETEC System Design — closing slide template

**Speaker notes (Arabic, 3 mandatory sections):**

## ما يقوله المتحدث
- شكراً لكم على وقتكم واهتمامكم. نَفتح الباب لأي سؤال أو ملاحظة.
- كل تعديل منهجي ذُكِر في العرض موثَّق بمبرره؛ كل مخرَج مَفهرَس مع شاهده في `evidence-map.json` المُرفق ضمن حزمة التقديم. نَستجيب لأي طلب توضيح إضافي بكامل الأمانة العلمية.

## الأنشطة الداخلية والأدلة الداعمة
- لا محتوى داخلي مخصص للشريحة الختامية. المتحدث يَستجيب من ذاكرة المحتوى (الشرائح 1–8) وفق نوع السؤال:
  - أسئلة على Cycle 1 → شريحة 4 + الملاحظات التحفظية فيها.
  - أسئلة على Cycle 2 → شريحة 6 + شريحة 5 (السياق التَمهيدي).
  - أسئلة على DOC-15 → شريحة 7.
  - أسئلة على الجاهزية → شريحة 8.
  - أسئلة على التَأطير العرفي للقيادة → شريحة 3 + شريحة 5 (T-CT-08).

## الملاحظات التحفظية (احتياطي عند السؤال)
- للأسئلة التي تَتجاوز نطاق العرض (مثلاً "كيف يَتم اختيار أداة الأرشفة؟"، "ما تكلفة الممارسة؟") — الردّ "هذا تفصيل تشغيلي خارج نطاق العرض الحالي؛ يُمكن الإحالة لقسم العمليات أو إدارة الميزانية إن استَلزَم".
- للأسئلة التي تَطلب التزاماً مُسَبَقاً ("هل تَلتزمون بإصدار X بحلول Y؟") — الردّ "حسب الجدول الزمني المُعتمَد في `timeline.json`، الإصدار مُخَطَّط له [التاريخ]. أي التزام إضافي يَستلزم مراجعة لجنة الحوكمة الداخلية للممارسة قبل الإجابة".

**Source traceability (for audit only — Claude Design ignores):**
- N/A — closing slide. المتحدث يَرسم من ذاكرة الشرائح 1–8.

---

## Brief metadata (audit only)

- **Brief generated:** 2026-05-04
- **Sprint reference:** Phase 2 / M3 tenant-side practice-scenario presentation content brief (per master plan §4)
- **Source narrative version:** v0.2 (timeline.json + scenario-narrative.md, both committed at `3741c8b` on `client/etec`)
- **DOC-15 schema version referenced:** v0.1 (fields.json on `origin/main` @ `7bcf5c4`, M3.1 sprint, 2026-05-04)
- **Total slides:** 9
- **Adjustments referenced:** أ, ب, ج, هـ (4 total — د is intentionally absent per v0.2)
- **Output target:** Claude Design → `.pptx` build using ETEC System Design brand template
- **Verification:** see sprint plan `C:\Users\USER\.claude\plans\delightful-launching-moth.md` §Verification

**End of brief.**

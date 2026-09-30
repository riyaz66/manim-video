import sys
from pptx import Presentation

for path in sys.argv[1:]:
    print("=" * 8, path)
    prs = Presentation(path)
    print(f"size_in: {prs.slide_width / 914400:.3f} x {prs.slide_height / 914400:.3f}"
          f"  slides: {len(prs.slides)}")
    total_pics, odd = 0, 0
    for i, s in enumerate(prs.slides, 1):
        texts, pics, links = [], 0, 0
        for sh in s.shapes:
            if sh.shape_type == 13:
                pics += 1
            if sh.has_text_frame:
                t = sh.text_frame.text.strip().replace("\n", " | ")
                if t:
                    texts.append(t)
            try:
                if sh.click_action.target_slide is not None:
                    links += 1
            except Exception:
                pass
            if sh.has_text_frame:
                for para in sh.text_frame.paragraphs:
                    for r in para.runs:
                        try:
                            if r.hyperlink.target_slide is not None:
                                links += 1
                        except Exception:
                            pass
        notes = ""
        try:
            notes = s.notes_slide.notes_text_frame.text[:60].replace("\n", " | ")
        except Exception:
            pass
        head = texts[0][:76] if texts else "(frame image)"
        total_pics += pics
        if pics and texts:
            odd += 1
        if i <= 5 or i == len(prs.slides):
            print(f"s{i}: pics={pics} links={links} :: {head}")
            if notes:
                print(f"      notes: {notes}")
        elif i == 6:
            print("      ... (middle slides omitted) ...")
    print(f"TOTAL pics={total_pics} slides={len(prs.slides)}"
          + (f"  slides_with_text={odd}" if odd else ""))

"""Tests for test rag evaluation contract.
اختبارات المشروع التي تثبت contracts وحدود الطبقات وسلوك workflow الظاهر في أسماء الاختبارات وimports.

الموقع في المعمارية: Test suite.
يُستدعى بواسطة: pytest أو أدوات acceptance.
يعتمد مباشرة على: لا توجد imports داخلية مباشرة ظاهرة.
الحد المعماري: لا يضيف هذا الملف production behavior؛ يثبت behavior قائمًا.
سير البيانات المختصر: يجهز هذا الملف مدخلاته، يشغل العملية المحددة، ثم يعيد
نتيجة CLI/evaluation أو assertion إلى caller.
"""
import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_hybrid_does_not_use_rrf_as_vector_similarity():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_hybrid_does_not_use_rrf_as_vector_similarity؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    source = (
        ROOT
        / "app/capabilities/analysis/retrieval/hybrid_retriever.py"
    ).read_text(encoding="utf-8")

    assert "vector_score=candidate.vector_score" in source
    assert "score=candidate.rrf_score" in source


def test_orchestrator_persists_vector_similarity_not_rrf():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_orchestrator_persists_vector_similarity_not_rrf؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    source = (
        ROOT
        / "app/capabilities/analysis/analysis_orchestrator.py"
    ).read_text(encoding="utf-8")

    assert "retrieved_contexts[0].vector_score" in source
    assert '"similarity_score": item.vector_score' in source


def test_vector_repository_filters_before_limit():
    """
    يثبت contract محددًا من خلال حالة اختبار معزولة ضمن طبقة Test suite.

    تُستدعى عندما يصل المسار إلى test_vector_repository_filters_before_limit؛ المدخلات المهمة: لا توجد مدخلات موضعية مهمة.
    تعيد نتيجة العملية الحالية أو تسجل/ترجع الأثر الذي يحدده هذا الـworkflow. يفشل الاختبار عند خرق الـcontract.
    """
    path = (
        ROOT
        / "app/infrastructure/database/repositories/retrieval_repository.py"
    )
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    distance_filter = "distance <= maximum_distance"
    limit_call = ".limit(limit)"

    matching_methods = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            continue

        segment = ast.get_source_segment(source, node)

        if (
            segment
            and distance_filter in segment
        ):
            matching_methods.append(
                (node.name, segment)
            )

    assert len(matching_methods) == 1

    method_name, method_source = matching_methods[0]

    assert distance_filter in method_source
    assert limit_call in method_source
    assert (
        method_source.index(distance_filter)
        < method_source.index(limit_call)
    ), (
        f"{method_name}: vector distance filter must be applied "
        "before limit within the same repository method"
    )

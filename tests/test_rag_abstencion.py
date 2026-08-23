from src.rag.retriever import RetrieverPoliticas


def test_abstencion_cuando_no_hay_evidencia():
    retriever = RetrieverPoliticas()

    # Pregunta que NO está en las políticas
    pregunta = "¿Cuál es la receta de la pizza margarita de la cafetería?"

    resultado = retriever.consultar(pregunta)

    assert resultado.tiene_evidencia is False
    assert len(resultado.citas) == 0
    assert "no tengo evidencia" in resultado.respuesta.lower() or \
           "no tengo evidencia suficiente" in resultado.respuesta.lower()
    assert resultado.mensaje_abstencion is not None
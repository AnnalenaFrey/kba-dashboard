from kba_dashboard.processing import KNOWN_BRAND_TYPOS, MULTI_WORD_BRANDS, extract_brand_and_model, read_excel

def test_extract_brand_and_model_single_name_brand_and_model():

    model_series = "opel astra"

    brand, model = extract_brand_and_model(model_series)

    assert brand == "OPEL"
    assert model == "ASTRA"

def test_extract_brand_and_model_single_name_brand_multiword_model():

    model_series = "byd dolphin surf"

    brand, model = extract_brand_and_model(model_series)

    assert brand == "BYD"
    assert model == "DOLPHIN SURF"

def test_extract_brand_and_model_multiword_brand():

    model_series = "alfa romeo stelvio"

    brand, model = extract_brand_and_model(model_series)

    assert brand == "ALFA ROMEO"
    assert model == "STELVIO"

import pandas as pd
from flask import make_response


# Turn an array of dictionaries usually returned as json,
# as a csv created by pandas instead.
def array_to_csv_flask_response(response_array):
    df = pd.DataFrame(response_array)
    response = make_response(df.to_csv())
    response.headers["Content-Disposition"] = \
        "attachment; filename=export.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

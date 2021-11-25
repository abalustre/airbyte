from datetime import datetime
from dateutil.relativedelta import relativedelta


class ParsePath:
    def __init__(self, path: str = None ,params: list = None):
        self._path = path
        self.params = params
        self._parse_paramns()
        self._parse_config()
    
    @property
    def formated_path(self) -> str:
        if not self.params:
            return self._path
        try:
            return self._path.format(*self.list_words_to_replace)
        except KeyError as e:
            raise KeyError(f"Variable {e} not informed in paramns")
        except ValueError as e:
            if e.args[0] == "cannot switch from manual field specification to automatic field numbering":
                raise ValueError("The path need a word between {}.")
        except Exception as e:
            raise e

    def _parse_paramns(self):
        for i,row in enumerate(self.params):
            if row["type"] == "date":
                variable = row["variable"]
                if "{" + str(variable) + "}" in self._path:
                    self._path = self._path.replace("{"+str(variable)+ "}","{"+str(i)+"}")
                else:
                    raise Exception(f"variable {variable} not informed in the URL")
            elif row["type"] == "period":
                start_variable = row["start_date"]["variable"]
                end_variable = row["end_date"]["variable"]
                if "{" + str(start_variable) + "}" in self._path:
                    self._path = self._path.replace("{"+str(start_variable)+ "}","{"+str(i)+"}")
                else:
                    raise Exception(f"variable {start_variable} not informed in the URL")
                if "{" + str(end_variable) + "}" in self._path:
                    self._path = self._path.replace("{"+str(end_variable)+ "}","{"+str(i+1)+"}")
                else:
                    raise Exception(f"variable {end_variable} not informed in the URL")
            else:
                raise Exception("type not valid")
    
    def _parse_config(self):
        try:
            words_to_replace = []
            for param in self.params:
                if param["type"] == "date":
                        value = self._get_value(param["value"], param["unit"]).strftime(param["format"])
                        words_to_replace.append(value)
                elif param["type"] == "period":
                    start_value = self._get_value(param["start_date"]["value"], param["unit"]).strftime(param["format"])
                    words_to_replace.append(start_value)
                    end_value = self._get_value(param["end_date"]["value"], param["unit"]).strftime(param["format"])
                    words_to_replace.append(end_value)

                else:
                    raise Exception("type not valid")
            self.list_words_to_replace = words_to_replace
        except Exception as e:
            raise e
    
    def _is_valid_value(self, value):
        if value == "current":
            return True
        elif len(value.split(" ")) == 3:
            _value = value.replace("current ", "")
            if "-" in _value and _value.replace("- ", "").isdigit():
                return True
            elif "+" in _value and _value.replace("+ ", "").isdigit():
                return True
        return False

    def _get_value(self, value, unit):
        if self._is_valid_value(value):
            if value == "current":
                return datetime.today()
            elif "-" in value:
                digit = int(value.replace("current - ", ""))
                if unit == "day":
                    return datetime.today() - relativedelta(days = digit)
                if unit == "month":
                    return datetime.today() - relativedelta(months = digit)
                if unit == "year":
                    return datetime.today() - relativedelta(years = digit)
            elif "+" in value:
                digit = int(value.replace("current + ", ""))
                if unit == "day":
                    return datetime.today() + relativedelta(days = digit)
                if unit == "month":
                    return datetime.today() + relativedelta(months = digit)
                if unit == "year":
                    return datetime.today() + relativedelta(years = digit)

        raise Exception("Params malformed")  
# Abalustre Airbyte's connectors

This document list all Abalustre Airbyte's connectors and how to install them.

## Install Airbyte's connector

1 - Login in Airbyte

2 - Navigate to Settings on the sidebar

3 - Navigate to Sources in the internal menu

4 - Click on the button `+ New Connector` on the top right

5 - Fill in the formulary fields

[Here](https://docs.airbyte.io/integrations/custom-connectors#adding-your-connectors-in-the-ui) is the Airbyte's documentation to install connectors.


## Abalustre connectors

### HTTP Request

This connector makes HTTP requests allowing the user to configure dates and dates period as variables.

**Path**: airbyte/airbyte-integrations/connectors/source-http-request

**Docker image**: Execute inside the connector path the command:
```bash
docker build . -t airbyte/source-http-request:0.1.0
```

**New connector form**
|                             |                             |  
| --------------------------- | --------------------------- |
| Connector display name      | HTTP Request                |
| Docker repository name      | airbyte/source-http-request |
| Docker image tag            | 0.1.0                       |
| Connector Documentation URL | None                        |

#### How to use it?

The HTTP Request connector has the following fields:

**url**: The URL that will be requested

**http_method**: The HTTP method which can be GET or POST

**headers**: The header for the HTTP Request

**body**: The body for the HTTP Request if the method is POST

**params**: The params are the variables that will be replaced in the URL for the HTTP Request

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The params can be a date or a period. It is an array of JSON data with the information:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Date JSON**:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**type**: It is always `date`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**unit**: It can be one of the values `year`, `month`, or `day`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**format**: It is the [date format](https://www.geeksforgeeks.org/python-strftime-function/)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**variable**: It is the variable name

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**value**: It is the variable value which can be:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current` => current date
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current + n` => current date + a number that represents the field unit
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current - n` => current date - a number that represents the field unit

```json
[{"type": "date", "unit": "month", "format": "%Y%m", "variable": "month_year", "value":  "current"}]
```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Period JSON**:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**type**: It is always `period`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**unit**: It can be one of the values `year`, `month`, or `day`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**format**: It is the [date format](https://www.geeksforgeeks.org/python-strftime-function/)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**start_date**: It is the JSON with the first date

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**end_date**: It is the JSON with the second date

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**variable**: It is the variable name

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**value**: It is the variable value which can be:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current` => current date
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current + n` => current date + a number that represents the field unit
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current - n` => current date - a number that represents the field unit

```json
[{"type": "period", "unit": "day", "format": "%m-%d-%Y", "start_date": {"variable": "from", "value": "current - 1"}, "end_date": {"variable": "to", "value": "current + 1"}}]
```

**response_format**: It is the response format that can be `csv` or `json`

**response_delimiter**: It is the response delimiter when the format is `csv`



##### Example Date:

&nbsp;&nbsp;&nbsp;&nbsp;**url**: http://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{month_year}.csv

&nbsp;&nbsp;&nbsp;&nbsp;**http_method**: GET

&nbsp;&nbsp;&nbsp;&nbsp;**params**: [{"type": "date", "unit": "month", "format": "%Y%m", "variable": "month_year", "value": "current"}]

&nbsp;&nbsp;&nbsp;&nbsp;**response_format**: csv

&nbsp;&nbsp;&nbsp;&nbsp;**response_delimiter**: ;



##### Example Period:

&nbsp;&nbsp;&nbsp;&nbsp;**url**: https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@moeda='AUD'&@dataInicial='{from}'&@dataFinalCotacao='{to}'&$format=json

&nbsp;&nbsp;&nbsp;&nbsp;**http_method**: GET

&nbsp;&nbsp;&nbsp;&nbsp;**params**: [{"type": "period", "unit": "day", "format": "%m-%d-%Y", "start_date": {"variable": "from", "value": "current - 1"}, "end_date": {"variable": "to", "value": "current + 1"}}]

&nbsp;&nbsp;&nbsp;&nbsp;**response_format**: json

<br></br>
****
### GraphQL Request

This connector makes GraphQL requests allowing the user to configure queries and input filters as variables.

**Path**: airbyte/airbyte-integrations/connectors/source-graphql

**Docker image**: Execute inside the connector path the command:
```bash
docker build . -t airbyte/source-graphql:0.1.0
```

**New connector form**
|                             |                             |  
| --------------------------- | --------------------------- |
| Connector display name      | GraphQL Request             |
| Docker repository name      | airbyte/source-graphql      |
| Docker image tag            | 0.1.0                       |
| Connector Documentation URL | None                        |

#### How to use it?

The GraphQL Request connector has the following fields:

**url**: The URL that will be requested

**http_method**: The HTTP method which can be GET or POST

**api_key**: The api_key for the GraphQL Request

**api_key_name**: The api_key_name for the GraphQL Request

**query**: The input query for the GraphQL Request

**variables**: The input variables for the GraphQL query

**headers**: The header for the GraphQL Request

**params**: The params are the variables that will be replaced in the URL for the GraphQL Request

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The params can be a date or a period. It is an array of JSON data with the information:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Date JSON**:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**type**: It is always `date`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**unit**: It can be one of the values `year`, `month`, or `day`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**format**: It is the [date format](https://www.geeksforgeeks.org/python-strftime-function/)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**variable**: It is the variable name

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**value**: It is the variable value which can be:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current` => current date
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current + n` => current date + a number that represents the field unit
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current - n` => current date - a number that represents the field unit

```json
[{"type": "date", "unit": "month", "format": "%Y%m", "variable": "month_year", "value":  "current"}]
```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**Period JSON**:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**type**: It is always `period`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**unit**: It can be one of the values `year`, `month`, or `day`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**format**: It is the [date format](https://www.geeksforgeeks.org/python-strftime-function/)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**start_date**: It is the JSON with the first date

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**end_date**: It is the JSON with the second date

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**variable**: It is the variable name

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**value**: It is the variable value which can be:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current` => current date
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current + n` => current date + a number that represents the field unit
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- `current - n` => current date - a number that represents the field unit

```json
[{"type": "period", "unit": "day", "format": "%m-%d-%Y", "start_date": {"variable": "from", "value": "current - 1"}, "end_date": {"variable": "to", "value": "current + 1"}}]
```

**json_source**: The json_source for the GraphQL response

**json_field**: The json_field for the GraphQL response


##### Example with Period:

&nbsp;&nbsp;&nbsp;&nbsp;**url**: https://md.uat.idealtech.services/

&nbsp;&nbsp;&nbsp;&nbsp;**http_method**: POST

&nbsp;&nbsp;&nbsp;&nbsp;**api_key**: tPS4XotJcf4DcW74vU6Z6ajtqcLwJs0z9A8gia52

&nbsp;&nbsp;&nbsp;&nbsp;**api_key_name**: x-api-key

&nbsp;&nbsp;&nbsp;&nbsp;**query**: query ($ticker: String!, $startDate: DateTime!, $endDate: DateTime) { tickerQuotes( ticker: $ticker startDate: $startDate endDate: $endDate) { totalCount nodes { tradeDate open close high low averagePrice numberOfTrades totalQuantity financialVolume bestBid bestAsk adjOpen adjClose adjHigh adjLow adjAveragePrice } } }

&nbsp;&nbsp;&nbsp;&nbsp;**variables**: {\"ticker\": \"PETR4\"}

&nbsp;&nbsp;&nbsp;&nbsp;**params**: [{\"type\": \"period\", \"unit\": \"day\", \"format\": \"%Y-%m-%d\", \"start_date\": {\"variable\": \"startDate\", \"value\": \"current - 2\"}, \"end_date\": {\"variable\": \"endDate\", \"value\": \"current\"}}]

&nbsp;&nbsp;&nbsp;&nbsp;**json_source**: field

&nbsp;&nbsp;&nbsp;&nbsp;**json_field**: root.instruments.nodes


##### Example without Period:

&nbsp;&nbsp;&nbsp;&nbsp;**url**: https://swapi-graphql.netlify.app/.netlify/functions/index

&nbsp;&nbsp;&nbsp;&nbsp;**http_method**: POST

&nbsp;&nbsp;&nbsp;&nbsp;**query**: query Root($after: String, $first: Int) { allFilms(after: $after, first: $first) { pageInfo { hasNextPage hasPreviousPage startCursor endCursor } totalCount films { title episodeID openingCrawl director producers releaseDate } } }

&nbsp;&nbsp;&nbsp;&nbsp;**json_source**: field

&nbsp;&nbsp;&nbsp;&nbsp;**json_field**: root.allFilms.films
### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


## Validate that the user is between 0 and 65 years old
def validate_data(age, investment_amount, intent_request):
    if age is not None:
        age = int(age)
        if age > 65:
            return build_validation_result(
                False,
                'age',
                'You should be under 65 years old to use this service. '
                'Please enter a valid age.'
            )
        elif age < 21:
            return build_validation_result(
                False,
                'age',
                'You should be over 21 years old to use this service. '
                'Please enter a valid age.'
            )

    ## Validate that the investment amount is at least $5,000
    if investment_amount is not None:
        investment_amount = float(investment_amount)
        if investment_amount < 5000:
            return build_validation_result(
                False,
                'investmentAmount',
                'We ask a minimum investment of $5,000. '
                'Please enter a valid amount.'
            )
                
    ## Return True results if age or amount are valid
    return build_validation_result(True, None, None)


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]
    
    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.

        ### YOUR DATA VALIDATION CODE STARTS HERE ###
        
        ## Get all slots
        slots = get_slots(intent_request)
        
        ## Validate user's input using the validate_data function
        validation_result = validate_data(age, investment_amount, intent_request)
        
        ## If the data provided by the user is not valid,
        ## the elicitSlot dialog action is used to re-prompt
        ## for the first violation detected.
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None  ## Cleans invalid slot

            ## Returns an elicitSlot dialog to request new data for the invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )
        ### YOUR DATA VALIDATION CODE ENDS HERE ###

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    # Get the initial investment recommendation

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###
    if risk_level == 'None':
        return close(
            intent_request['sessionAttributes'],
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': """Thank you for answering my questions. 
                For a portfolio with virtually no risk but slower growth, 
                I recommend investing 100% into bonds like AGG.
                """
            }
        )
    if risk_level == 'Very Low':
        return close(
            intent_request['sessionAttributes'],
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': """Thank you for answering my questions. 
                For a portfolio with very low risk and conservative growth, 
                I recommend investing 80% into bonds like AGG, 
                and the remaining 20% into equities like SPY.
                """
            }
        )
    if risk_level == 'Low':
        return close(
            intent_request['sessionAttributes'],
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': """Thank you for answering my questions. 
                For a portfolio with low risk and moderately conservative growth, 
                I recommend investing 60% into bonds like AGG, 
                and the remaining 40% into equities like SPY.
                """
            }
        )        
    if risk_level == 'Medium':
        return close(
            intent_request['sessionAttributes'],
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': """Thank you for answering my questions. 
                For a portfolio with medium risk and moderate growth, 
                I recommend investing 60% into equities like SPY, 
                and the remaining 40% into bonds like AGG.
                """
            }
        )
    if risk_level == 'High':
        return close(
            intent_request['sessionAttributes'],
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': """Thank you for answering my questions. 
                For a portfolio with high risk and moderately aggressive growth, 
                I recommend investing 80% into equities like SPY, 
                and the remaining 20% into bonds like AGG.
                """
            }
        )
    if risk_level == 'Very High':
        return close(
            intent_request['sessionAttributes'],
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': """Thank you for answering my questions. 
                For a portfolio with very high risk and aggressive growth, 
                I recommend investing 100% into equities like SPY.
                """
            }
        )
    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###

    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)

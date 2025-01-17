def weather_info(location):
    return f"The weather in {location} is sunny and 75°F."

def news_summary(topic):
    return f"Here is the latest news on {topic}: ..."

def math_solver(expression):
    try:
        result = eval(expression)  # Use cautiously
        return f"The result of {expression} is {result}."
    except Exception as e:
        return f"Error solving the expression: {e}"

# Function mapping
function_mapping = {
    "weather": weather_info,
    "news": news_summary,
    "math": math_solver,
}

def call_function(function_name, args):
    """Call the appropriate function from the function mapping."""
    func = function_mapping.get(function_name)
    if func:
        try:
            result = func(*args)
            return result
        except Exception as e:
            return f"Error executing function '{function_name}': {e}"
    else:
        return f"Function '{function_name}' is not recognized."

# Example usage
print(call_function("weather", ["New York"]))  # Output: The weather in New York is sunny and 75°F.
print(call_function("math", ["5 + 3"]))        # Output: The result of 5 + 3 is 8.

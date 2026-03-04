from typing import Union

def classify_triangle(a: int, b: int, c: int) -> Union[str, None]:
    """
    Classify a triangle based on its side lengths.

    Parameters:
        a (int): length of side a
        b (int): length of side b
        c (int): length of side c

    Returns:
        str or None: classification of the triangle ("Not a triangle", "Equilateral", "Isosceles", or "Scalene")
    """
    if a <= 0 or b <= 0 or c <= 0:
        return "Not a triangle"
    if a + b <= c or a + c <= b or b + c <= a:
        return "Not a triangle"
    if a == b == c:
        return "Equilateral"
    elif a == b or b == c or a == c:
        return "Isosceles"
    else:
        return "Scalene"

if __name__ == "__main__":
    a,b,c = map(int, input("Enter the lengths of the sides of the triangle (separated by spaces): ").split())
    result = classify_triangle(a, b, c)
    print(f"The triangle is classified as: {result}")
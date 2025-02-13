from fleetenablechatbot.crew import PDFProcessingCrew


def run():
    """
    Main function to initialize and run the crew.
    It prompts the user for a query, then uses that query to search the PDF.
    The final markdown output is printed to the terminal and saved to output.md.
    """
    # Prompt the user for a query
    query = input("Enter your query: ")

    # Initialize the crew and update the query in the crew instance.
    pdf_crew = PDFProcessingCrew()
    pdf_crew.user_query = query  # Override the default query with the user's input

    # Kickoff the crew and collect the result
    result = pdf_crew.crew().kickoff()

    # Get the final output text (if result has a 'raw' attribute, use it; otherwise, use str(result))
    output_text = result.raw if hasattr(result, "raw") else str(result)

    # Print the result to the terminal
    print("\nCrew execution result (Markdown Output):")
    print(output_text)

    # Save the result to a markdown file
    output_filename = "output.md"
    with open(output_filename, "w") as f:
        f.write(output_text)
    print(f"\nOutput saved to {output_filename}")


if __name__ == "__main__":
    run()

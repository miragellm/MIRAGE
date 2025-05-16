# LLM-Agent with Imperfect Manuals (Web)


## Setup

Before you begin, you'll need to set up the environment following the instructions in the [WebArena repository](https://github.com/web-arena-x/webarena). This likely involves setting up necessary dependencies and potentially Docker.

**Environment Variables:**

Ensure you have the following environment variables set:

-   `SERVER_HOST`: The hostname or IP address of your web server.
-   `SERVER_PORT`: The port number your web server is running on.

You can typically set these in your shell environment or a `.env` file. For example:

```bash
export SERVER_HOST="localhost"
export SERVER_PORT="8000"
```

## Usage
Follow these steps to evaluate the imperfect manual:

1. Unpack Configuration:
Run the following script to unpack the configuration file:

```python
python scripts/generate_test_data.py
```

2. Prepare Demo Data:
Download the demo pickle files from [placeholder]. Then Move them into the `extracted_data` directory, and make sure to follow the following structure:
```
./extracted_data/
├── gitlab/
├── reddit/
├── shopping/
└── shopping_admin/
```

3. Run Evaluation:
Execute the main evaluation script with the desired model, result directory, and a note describing your experiment:

```python
python main.py --model gpt-4o --result_dir exp_logs --note "test"
```
Arguments:

--model: The name of the language model to use
--result_dir: The directory where evaluation results will be saved (e.g., exp_logs)
--note: A descriptive note or identifier for this evaluation run

4. View Results:
After the evaluation is complete, you will find the results in the directory specified by the --result_dir argument (e.g., exp_logs).

## Type of Imperfect Manual
## Imperfect Manual Styles


There are five distinct types of imperfect manual, as illustrated in the following table. While these can be generated on the fly by LLMs, we also provide a human-verified version, which can be downloaded from [placeholder].

| Imperfect Style          | Description                                                                                                                                                                                                                                                           |
| :----------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| UI Change                | Interactive element names are sometimes (but not always) changed. For example, 'search' might be changed to 'search here', while maintaining semantic similarity.                                                                                                     |
| Narrative                | Formatted actions in the manual are transformed into verbal language descriptions.                                                                                                                                                                                   |
| Narrative Merged         | Verbal language is used, and actions that occur on the same screen or within a short sequence are merged into a single sentence.                                                                                                                                      |
| Skip Step                | One or more steps in the original manual are omitted or skipped.                                                                                                                                                                                                   |
| Obs Delay                | The observation (e.g., the visual state of the web page) provided to the agent is delayed compared to the actual action taken. This means the agent might be acting based on a slightly outdated view of the environment.                                          |

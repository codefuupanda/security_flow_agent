{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "3781a789-f112-4d6b-9d8f-d2dfbc2deab3",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import json\n",
    "import os\n",
    "from pathlib import Path"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "d1c7cd47-5dee-416e-b3a8-373758ec43da",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Saved 2000 logs to C:\\Users\\arusi\\projects\\secuFlow-agent\\logs\\windows_logs.json\n"
     ]
    }
   ],
   "source": [
    "def prepare_windows_logs():\n",
    "    # Load the structured CSV using full absolute path\n",
    "    csv_path = r\"C:\\Users\\arusi\\projects\\secuFlow-agent\\data\\Windows_2k.log_structured.csv\"\n",
    "    df = pd.read_csv(csv_path)\n",
    "    \n",
    "    # Normalize / rename fields\n",
    "    df = df.rename(columns={\n",
    "        \"Timestamp\": \"timestamp\",\n",
    "        \"EventId\": \"event_id\",\n",
    "        \"Source\": \"source\",\n",
    "        \"Content\": \"message\",\n",
    "        \"TemplateId\": \"template_id\"\n",
    "    })\n",
    "    \n",
    "    # Convert to list of dicts\n",
    "    logs = df.to_dict(orient=\"records\")\n",
    "    \n",
    "    # Ensure everything is string (safe for LLM)\n",
    "    for entry in logs:\n",
    "        for k, v in entry.items():\n",
    "            entry[k] = str(v)\n",
    "    \n",
    "    # Save to logs/windows_logs.json\n",
    "    Path(r\"C:\\Users\\arusi\\projects\\secuFlow-agent\\logs\").mkdir(exist_ok=True)\n",
    "    \n",
    "    save_path = r\"C:\\Users\\arusi\\projects\\secuFlow-agent\\logs\\windows_logs.json\"\n",
    "    with open(save_path, \"w\", encoding=\"utf-8\") as f:\n",
    "        json.dump(logs, f, indent=2)\n",
    "    \n",
    "    print(f\"Saved {len(logs)} logs to {save_path}\")\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    prepare_windows_logs()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d826cea6-e73c-4453-9f94-46cbd4f3bf2a",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.21"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests


# In[2]:


standings_url = "https://fbref.com/en/comps/20/Bundesliga-Stats"


# In[3]:


data = requests.get(standings_url)


# In[4]:


from bs4 import BeautifulSoup


# In[5]:


soup = BeautifulSoup(data.text)
standings_table = soup.select('table.stats_table')[0]
links = standings_table.find_all('a')
links = [l.get("href") for l in links]
links = [l for l in links if '/squads/' in l]


# In[6]:


team_urls = [f"https://fbref.com{l}" for l in links]


# In[7]:


data = requests.get(team_urls[0])


# In[8]:


import pandas as pd
matches = pd.read_html(data.text, match="Scores & Fixtures")[0]


# In[9]:


soup = BeautifulSoup(data.text)
links = soup.find_all('a')
links = [l.get("href") for l in links]
links = [l for l in links if l and 'all_comps/shooting/' in l]


# In[10]:


data = requests.get(f"https://fbref.com{links[0]}")


# In[11]:


shooting = pd.read_html(data.text, match="Shooting")[0]


# In[12]:


shooting.head()


# In[13]:


shooting.columns = shooting.columns.droplevel()


# In[14]:


team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")


# In[15]:


team_data.head()


# In[16]:


years = list(range(2022, 2016, -1))
all_matches = []


# In[17]:


standings_url = "https://fbref.com/en/comps/20/Bundesliga-Stats"


# In[18]:


import time
for year in years:
    data = requests.get(standings_url)
    soup = BeautifulSoup(data.text)
    standings_table = soup.select('table.stats_table')[0]

    links = [l.get("href") for l in standings_table.find_all('a')]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]
    
    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com{previous_season}"
    
    for team_url in team_urls:
        team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
        data = requests.get(team_url)
        matches = pd.read_html(data.text, match="Scores & Fixtures")[0]
        soup = BeautifulSoup(data.text)
        links = [l.get("href") for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/shooting/' in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        shooting = pd.read_html(data.text, match="Shooting")[0]
        shooting.columns = shooting.columns.droplevel()
        try:
            team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
        except ValueError:
            continue
        team_data = team_data[team_data["Comp"] == "Bundesliga"]
        
        team_data["Season"] = year
        team_data["Team"] = team_name
        all_matches.append(team_data)
        time.sleep(1)


# In[19]:


len(all_matches)


# In[20]:


match_df = pd.concat(all_matches)


# In[21]:


match_df.columns = [c.lower() for c in match_df.columns]


# In[22]:


match_df


# In[23]:


match_df.to_csv("Bundesliga.csv")


# In[ ]:





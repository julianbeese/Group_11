### Day 2, Phase 1: Chronological info about the movies

Let's continue to expand the class.

- [ ] Define a new method called **releases** that receives a _genre_ argument with a default of **None**. If **None** is selected, the class should create a pandas dataframe with how many movies per year were released in total. Using _genre_ should filter only for the movies of that type.
- [ ] Make a second page for the streamlit app you are developping. It is going to be used for chronological info. Plot the output of the previous computed dataframe there i na **bar plot**. There should be an input in the streamlit app for the genre. It is OK to limit the genres into just 5-10 different ones, for time's sake.
- [ ] Define a new class mehtod called **ages**. It should receive a single argument of either 'Y', 'M', with 'Y' as default'. If 'Y', for year, is selected, you should compute in a dataframe how many births happend per year. If 'M', for Month, is selected, you should do same for Month of the Year. Please notice it is not Year-Month, but just Month. Someone born in **January 1920** should count towards the same bin as **January 2000**. If the user selects something else, default to Year.
- [ ] In the second page of your app, plot this info below the previous plot. Make a drop down to select the corresponding options.

### Day 2, Phase 2: Classification

- [ ] Make a third page for your app. In this page you are going to use a local LLM like we've seen in class to classify text. Choose a small model from [ollama](www.ollama.com) and add Documentation to your README on this prerequisite.
- [ ]$\times 3$ (_3 points_) In the third page of the app, include a button labeled **"Shuffle"** and three text boxes. In one box, you should print a random movie title and its summary. In the second box, print the genres for that movie contained in the database. Just the genres, not the dictionary itself. In the third box, you are going to print the genre classification your local LLM decided is has. Try to make your LLM to print only the genres. You will definetely need to configure your prompt to produce good results. Welcome to the world of [prompt engineering](https://en.wikipedia.org/wiki/Prompt_engineering)! If you are struggling with this part, please contact me.
- [ ] When the latter process runs, ask the LLM again if the genres it identified are contained in the list from the database. Congratulations, you most likely are now doing your **first AI pipeline**.Think and deploy of a way to identify a positive or negative answer.

Remember, when the button is pressed, you should select another random movie.  
It is OK if the Shuffle button does not work or is blocked during the thought process of the LLM.  
**You are not optimising for speed** (yet): it is OK if this process takes some time.  

### Day 2, Phase 3: Cleaning up

- [ ] Add a 'requirements.txt' file to your git repo with all the packages you used. This file will be used to generate an environment where your code will be ran. Remember to make it OS independent. Add instructions to README.md on how to install the packages. Write a small essay at the the end of your README.md on how you think the text classification of this project could help with the [UN's SDGs](https://sdgs.un.org/goals).

---
## Grading

Between the two parts, there are 20 gradable items in both Part 1 and 2. Every [] is 1 point out of 20.

<div class="alert alert-danger">
    <b> REMEMBER: IT IS OK TO PROTOTYPE CODE IN NOTEBOOKS OR OTHER FILES </b>
    <br>
    <b> The final delivery of the project is the app. </b>
    <br>
    <b> We will only consider contents in your "master" repository before the end of the deadline.</b>
</div>

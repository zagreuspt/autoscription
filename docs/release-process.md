# Release Process
### Reason:
This process is  to minimize bugs in production, having in mind the manual deployment
process and the relevant cost it generates for an update.

## Create a new release branch
Create branch using the following name pattern `release-x-x-x`
The numbering should follow the semantic versioning. More [here](https://www.geeksforgeeks.org/introduction-semantic-versioning/)

Example
```commandline
git checkout -b release-1-0-0
```

Once the branch is finalised and all the changes are in place.
A merge request should be opened targeting master.

All the team should be added as reviewers. Once the team approves
it the merge can be made if the following criteria are met.

### No broken tests
The changes do not make the test fail. Or the tests have been updated
as well.
```commandline
python -m unittest
```

### The application is package-able
The following command is successful. build and dist directories should be removed prior to the command
```commandline
pyinstaller .\autoscription_main.spec --noconfirm
```

### The application generates the same results
Using report generated once the flow is complete as reference.
The application should generate same or better results.
If the application is presenting worst results the release should be
stopped and further investigation should take place.

### Upload exe
Once the merge is complete a new version of the application executable should be
uploaded to sharepoint under the exe directory. The naming convention being
`autoscription-x-x-x.zip`. Example `autoscription-1-0-0.zip`
# CI/CD documentation and notes

## How to rollback the previous version of the app 
Situation: we deployed the app on prod but the users are complaining because of the bugs or other problems with the app. 
Solution: 
- Go to Jenkins → open the main pipeline job (build/deploy) → Build History on the left. Find the last build with a SUCCESS status (green) that ran BEFORE the problematic release. Open its Console Output and look for the line "Building commit XXXXXXXX" — that's the SHA you need (8 characters, e.g. 4f92ab12). Copy it.
- In the job list, find the job named "anime-backlog-rollback". Click into it, then on the left select "Build with Parameters" 
- The form will show a single text field, ROLLBACK_SHA. Paste in the SHA you copied in step 1 (no spaces, no quotes, exactly as it appeared in the log).
- Click "Build". If the build turns green (SUCCESS), the rollback completed successfully.

## Notes & Tips
Host key verification failed problem sulution: 

```sh
docker exec -it -u 1000:1000 jenkins bash

mkdir -p /var/jenkins_home/.ssh

chown -R 1000:1000 /var/jenkins_home/.ssh

ssh-keyscan -H [deployment_server_ip] >> ~/.ssh/known_hosts

chmod 600 ~/.ssh/known_hosts 
```
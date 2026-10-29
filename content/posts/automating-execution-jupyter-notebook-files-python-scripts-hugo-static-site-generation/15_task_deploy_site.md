```python
# def task_deploy_site():
#     """Prompt for a commit message and push to GitHub"""
#     def commit_and_push():
#         message = input("What is the commit message? ")
#         if not message.strip():
#             print("❌ Commit message cannot be empty.")
#             return 1  # signal failure

#         # Stage and commit all changes
#         subprocess.run(["git", "add", "."], check=True)
#         subprocess.run(["git", "commit", "-am", message], check=True)
#         print("✅ All files committed. Run 'git push' to push to GitHub.")
        
#         subprocess.run(["git", "push"], check=True)
#         print("✅ Pushed to GitHub.")

#     return {
#         "actions": [commit_and_push],
#         "task_dep": ["build_site"],
#         "verbosity": 2,
#         "clean": [],  # Don't clean these files by default.
#     }
```
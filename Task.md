# BLUQUIST Backend Task

## Introduction

Provided with this task, you receive a minimal Python Flask application with a very basic user management module. Your task is to extend this application and add support for teams. A team is a group of users. A user can be part of multiple teams. A team has a name, and at least one user. Users can have one of two roles in a team: Admin or member. A team admin is the only one that can change the team name, add and remove users and change the role of users in the team. All users in a team can see all other users and their roles in the team.

You are free in how you structure the required functionality and how you define the endpoints.

The task is designed to touch all aspects of the application: Create database models, create a team controller, a team route with necessary endpoints, have access control on the endpoints and create an OpenAPI specification for the implementation. The goal is not to have a perfect deployment-ready team component, but to show knowledge of the technology-stack and the ability to understand requirements and write and structure code. Therefore it is totally okay, when not all aspects of the team management are fully implemented. However, please *leave comments* that show which parts have been left out purposefully.

You shouldn't spend more than 2-3h on this task.

## Requirements

Implement the following functionality:
- Any user can create a team. A team must have a name. The user that creates a team is automatically added as an admin of the team.
- A team admin can: Rename the team, add and remove users, delete a team and change the role of a user in a team (to `admin` or `member`)
- Any user in a team can see all other users within the team and their roles
- There should be an endpoint to list all teams that a user is part of. 
- A user with the system role `UserRole.ADMIN` should be able to access any team as if they were a team admin, even when they are not part of a team.

Technical requirements:
- All user input to any endpoint must be validated
- Extend the OpenAPI specification with all implemented endpoints

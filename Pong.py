import pygame
import time
import random
import math

from pygame import mixer


class Ball():
     def __init__(self, x, y, size, speed):
          self.size = size
          self.x = x
          self.y = y
          self.velX = random.choice([-1, 1]) * speed # Either goes left or right randomly
          self.velY = (random.random()*2-1)  * speed # This speed might need to be adjusted
          self.speed = speed
     
     def draw(self, screen):
          pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.size)
     
     def move(self, dt):
          self.x += self.velX * dt
          self.y += self.velY * dt
     
     def windowCollisionY(self, sound):
          # We only care about the floor and the ceiling
          # First, the ceiling
          if self.y - self.size <= 0: # The ceiling is y = 0
               self.y = self.size # Make sure we don't intersect the wall
               self.velY = abs(self.velY) # Make the velocity positive
               sound.play()
          
          # Then, the floor
          if self.y + self.size >= pygame.display.get_window_size()[1]: # y-coordinate of the window
               self.y = pygame.display.get_window_size()[1] - self.size
               self.velY = abs(self.velY) * -1
               sound.play()


     def isWindowCollisionX(self):
          # Let's ignore the radius here
          if self.x < 0:
               return "right"
          if self.x > pygame.display.get_window_size()[0]:
               return "left"
          else:
               return None

     def accelerate(self, amount):
          if self.velX < 0:
               self.velX -= amount
          else:
               self.velX += amount

     def reset(self, x, y, speed):
          self.velX = random.choice([-1, 1]) * speed # Either goes left or right randomly
          self.velY = (random.random()*2-1)  * speed # This speed might need to be adjusted
          self.x = x
          self.y = y
     

class Paddle():
     def __init__(self, centerX, centerY, width, height, speed):
          self.centerX = centerX
          self.centerY = centerY
          self.height = height
          self.width = width
          self.coordinates = [centerX - (width/2), centerY - (height/2)] # Some calculation to get the actual coordinates
          self.speed = speed

     
     def draw(self, screen):
          paddle_rect = pygame.Rect(self.coordinates[0], self.coordinates[1], self.width, self.height) # Create the rectangel with coordinates and size (width and height)
          pygame.draw.rect(screen, (255, 255, 255), paddle_rect) # Draw the rectangel on the screen, with some color and which rectangel
     
     def move(self, direction, dt): # Direction will be either 1, -1 or 0
          # The same change need to be applied to the center and the coordinates
          change = self.speed * direction * dt
          self.centerY += change
          self.coordinates[1] += change
     
     def checkCollision(self, ball, sound):
          # Distance between the paddle and the ball
          # Note that this shoudl work regardless of which direction
          distanceX = abs(self.centerX - ball.x) - ball.size - self.width/2 # Also uses the radius of the ball and the iwdth of the paddle
          distanceY = abs(self.centerY - ball.y) - ball.size - self.height/2
          if distanceX <= 0 and distanceY <= 0:
               sound.play()
               # Flip the x-direction and make a tiny change to the y-direction for spicyness
               # ball.velX *= -1
               ball.velY += (random.random()*2-1) * 300 # Change this for spicyness

               # To move the ball out of the way, we are gonna spagetti this to figure out which side
               # the ball is on and get it on the inner edge of the paddle
               if ball.x > pygame.display.get_window_size()[1]/2:
                    ball.x = self.centerX - self.width*1.3 # this is ugly
                    ball.velX = abs(ball.velX) * -1
               else:
                    ball.x = self.centerX + self.width*1.3
                    ball.velX = abs(ball.velX)
               ball.accelerate(50)
     
     def reset(self, x, y):
          self.centerX = x
          self.centerY = y
          self.coordinates = [self.centerX - (self.width/2), self.centerY - (self.height/2)]
          


class Pong():
     def __init__(self, leftPaddle, rightPaddle, ball):
          # Initialize pygame and the screen
          pygame.init()
          self.screen = pygame.display.set_mode((1200, 800))

          self.leftPaddle = leftPaddle
          self.leftPaddle_defaultX = leftPaddle.centerX
          self.leftPaddle_defaultY = leftPaddle.centerY
          self.leftPaddle_score = 0

          self.rightPaddle = rightPaddle
          self.rightPaddle_defaultX = rightPaddle.centerX
          self.rightPaddle_defaultY = rightPaddle.centerY
          self.rightPaddle_score = 0

          self.ball = ball
          self.ball_defaultX = ball.x
          self.ball_defaultY = ball.y
          self.ball_defaultSpeed = ball.speed

          self.font = pygame.font.Font("freesansbold.ttf", 32)
          self.PaddleHit_sound = mixer.Sound("Silas Projects/Games/Pong/PaddleHit.wav")
          self.WallHit_sound = mixer.Sound("Silas Projects/Games/Pong/WallHit.wav")
          self.roundOver_sound = mixer.Sound("Silas Projects/Games/Pong/RoundOver.wav")
     
     def updateScore(self, winner, sound):
          sound.play()
          if winner == "left":
               self.leftPaddle_score += 1
          else:
               self.rightPaddle_score += 1
     
     def showScore(self):
          leftScore_text = self.font.render(str(self.leftPaddle_score), True, (255, 255, 255))
          rightScore_text = self.font.render(str(self.rightPaddle_score), True, (255, 255, 255))

          self.screen.blit(leftScore_text, (100, 20))
          self.screen.blit(rightScore_text, (pygame.display.get_window_size()[0]-100, 20))


     def play(self):
          last_time = time.time()
          game_running = True

          leftPaddle_direction = 0
          rightPaddle_direction = 0

          while game_running:
               # Make sure to calculate delta time
               dt = time.time() - last_time
               last_time = time.time()

               for event in pygame.event.get():
                    # Close the program if the player presses X
                    if event.type == pygame.QUIT:
                         game_running = False
                    
                    if event.type == pygame.KEYDOWN:
                         if event.key == pygame.K_UP:
                              rightPaddle_direction = -1
                         if event.key == pygame.K_DOWN:
                              rightPaddle_direction = 1
                         if event.key == pygame.K_w:
                              leftPaddle_direction = -1
                         if event.key == pygame.K_s:
                              leftPaddle_direction = 1
                    
                    if event.type == pygame.KEYUP:
                         if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                              rightPaddle_direction = 0
                         if event.key == pygame.K_w or event.key == pygame.K_s:
                              leftPaddle_direction = 0
               
               # Paddle and ball movement
               self.rightPaddle.move(rightPaddle_direction, dt)
               self.leftPaddle.move(leftPaddle_direction, dt)
               self.ball.move(dt)

               # Check collisions with the paddle and the window edges
               self.rightPaddle.checkCollision(self.ball, self.PaddleHit_sound)
               self.leftPaddle.checkCollision(self.ball, self.PaddleHit_sound)
               self.ball.windowCollisionY(self.WallHit_sound)

               # Check if the ball went into someones court
               winner = self.ball.isWindowCollisionX()
               if winner: # Check that this does not equal to None
                    self.updateScore(winner, self.roundOver_sound)

                    self.ball.reset(self.ball_defaultX, self.ball_defaultY, self.ball_defaultSpeed)
                    self.leftPaddle.reset(self.leftPaddle_defaultX, self.leftPaddle_defaultY)
                    self.rightPaddle.reset(self.rightPaddle_defaultX, self.rightPaddle_defaultY)
          

               # Update the display
               self.screen.fill((0, 0, 0))
               # Draw the shapes
               self.leftPaddle.draw(self.screen)
               self.rightPaddle.draw(self.screen)
               self.ball.draw(self.screen)
               self.showScore()
               # Update the display
               pygame.display.update()
               # If there was a previous winner, make a pause
               if winner:
                    time.sleep(1)
                    last_time = time.time() # Update the time after the sleep


if __name__ == "__main__":
     leftPlayer = Paddle(40, 400, 20, 150, 500)
     rightPlayer = Paddle(1160, 400, 20, 150, 500)
     ball = Ball(600, 400, 15, 400)
     game = Pong(leftPlayer, rightPlayer, ball)
     game.play()

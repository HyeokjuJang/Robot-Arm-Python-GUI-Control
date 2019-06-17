#define X_STEP_PIN         13
#define X_DIR_PIN          12
#define X_ENABLE_PIN       8

#define Y_STEP_PIN         7
#define Y_DIR_PIN          4
#define Y_ENABLE_PIN       2

int step_x = 0;
int step_y = 0;
void step_move(int x,int y);

void setup() {
  Serial.begin(9600);
  
  pinMode(X_STEP_PIN  , OUTPUT);
  pinMode(X_DIR_PIN    , OUTPUT);
  pinMode(X_ENABLE_PIN    , OUTPUT);
  
  pinMode(Y_STEP_PIN  , OUTPUT);
  pinMode(Y_DIR_PIN    , OUTPUT);
  pinMode(Y_ENABLE_PIN    , OUTPUT);
  
  digitalWrite(X_ENABLE_PIN    , LOW);
  digitalWrite(Y_ENABLE_PIN    , LOW);
}

void loop () {
  if(Serial.available()){
    char o = Serial.read();
    if(o == 'H'){
      //go home
      Serial.print("going Home\n");
    }else if(o == 'G'){
      //step_move
      int x=Serial.parseInt();
      int y=Serial.parseInt();
      int d_x = x-step_x;
      int d_y = y-step_y;
    
      step_move(d_x,d_y);
      step_x=x;
      step_y=y;
      
      Serial.print("done\n");
    }else{
      Serial.print("what is wrong?\n");
    }
  }  
  
}

void step_move(int x,int y){
  int i=0;
  int max_step=0;
  int x_count=0;
  int y_count=0;
  if (x>0) {
    digitalWrite(X_DIR_PIN    , HIGH);
  }else {
    digitalWrite(X_DIR_PIN    , LOW);
    x = -x;
  }
  if(y>0){
    digitalWrite(Y_DIR_PIN    , HIGH);
  }else{
    digitalWrite(Y_DIR_PIN    , LOW);
    y=-y;
  }
  if(x<y){
    max_step=y;
  }else{
    max_step=x;
  }
  for(i=0;i<max_step;i++){
    if(x_count<x){
      digitalWrite(X_STEP_PIN    , HIGH);
    }
    if(y_count<y){
      digitalWrite(Y_STEP_PIN    , HIGH);
    }
    delay(3);
    digitalWrite(X_STEP_PIN    , LOW);
    digitalWrite(Y_STEP_PIN    , LOW);
    
    
    x_count++;
    y_count++;
  }
}



#include<stdio.h>
#include<stdlib.h>
struct node
{
	int data;
	struct node *next;
};
struct node *head=NULL;
struct node *createnode(int data)
{
	struct node *newnode;
	newnode=(struct node*)malloc(sizeof(struct node));
	newnode->data=data;
	newnode->next=NULL;
};
void insert_at_beg(int data)
{
	struct node *newnode=createnode(data);
	if(head==NULL)
	{
		head=newnode;
	}
	else
	{
		newnode->next=head;
		head=newnode;
	}
}
void insert_at_end(int data)
{
	struct node *newnode=createnode(data);
	if(head==NULL)
	{
		head=newnode;
	}
	else
	{
		struct node *temp=head;
		while(temp->next!=NULL)
		{
			temp=temp->next;
		}
		temp->next=newnode;
	}
}
void delete_at_beg()
{
	if(head==NULL)
	{
		printf("deletion is not possible\n");
		return;
	}
	else
	{
		head=head->next;
	}
}
void delete_at_end()
{
	if(head==NULL)
	{
		printf("deletion is not possible\n");
		return;
	}
	else
	{
		struct node *temp=head;
		while(temp->next->next!=NULL)
		{
			temp=temp->next;
		}
		temp->next=NULL;
	}
}
void insert_at_part_pos(int pos, int data)
{
	struct node *newnode=createnode(data);
	if(head==NULL)
	{
		head=newnode;
		return;
	}
	if(pos==0)
	{
		newnode->next=head;
		head=newnode;
		return;
	}
	int i;
	struct node *temp=head;
	for(i=0;i<pos-1;i++)
	{
		temp=temp->next;
	}
	newnode->next=temp->next;
	temp->next=newnode;
}
void display()
{
	if(head==NULL)
	{
		printf("List is Empty\n");
	}
	else
	{
		struct node *temp=head;
		while(temp!=NULL)
		{
			printf("%d ",temp->data);
			temp=temp->next;
		}
		printf("\n");
	}
}
int main()
{
	int ch;
	while(1)
	{
		printf("1.insert at beg 2.insert at end  3.display 4.deletion at beg 5.deletion at end 6.insert at particular position\n");
		scanf("%d",&ch);
		if(ch==1)
		{
			int data;
			scanf("%d",&data);
			insert_at_beg(data);
		}
		else if(ch==2)
		{
			int data;
			scanf("%d",&data);
			insert_at_end(data);
		}
		else if(ch==3)
		{
			display();
		}
		else if(ch==4)
		{
			delete_at_beg();
		}
		else if(ch==5)
		{
			delete_at_end();
		}
		else if(ch==6)
		{
			int pos,value;
			scanf("%d%d",&pos,&value);
			insert_at_part_pos(pos,value);
		}
		else
		{
			break;
		}
	}
}